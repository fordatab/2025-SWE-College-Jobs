import re

def extract_tables(md_content):
    lines = md_content.splitlines()
    tables = {}
    current_section = None
    table_data = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('### '):
            if current_section and table_data:
                tables[current_section] = table_data
            current_section = stripped[4:].strip()
            in_table = False
            table_data = []
        if stripped.startswith('|'):
            row = [c.strip() for c in line.split('|')[1:-1]]
            if not in_table:
                in_table = True
                table_data.append(row)  # headers
            else:
                table_data.append(row)
        elif in_table and not stripped:
            in_table = False
    if current_section and table_data:
        tables[current_section] = table_data
    return tables

def generate_md_table(headers, rows):
    md = '| ' + ' | '.join(headers) + ' |\n'
    md += '| ' + ' | '.join('---' for _ in headers) + ' |\n'
    for row in rows:
        md += '| ' + ' | '.join(row) + ' |\n'
    return md

def get_url(cell):
    match = re.search(r'\[.*?\]\((https?://[^)]*)\)', cell)
    return match.group(1) if match else ''

with open('README.md', 'r', encoding='utf-8') as f:
    readme_content = f.read()

source_tables = extract_tables(readme_content)

try:
    with open('my-tracking.md', 'r', encoding='utf-8') as f:
        tracking_content = f.read()
    tracking_tables = extract_tables(tracking_content)
except FileNotFoundError:
    tracking_tables = {}

output_md = '# 2025 SWE College Jobs - My Tracking\n\n'
output_md += 'This file is automatically updated daily from README.md, preserving your application statuses.\n\n'
output_md += '## 2025 USA SWE Internships 📚🦅\n\n'

sections = ['FAANG+', 'Quant', 'Other']
for section in sections:
    if section not in source_tables:
        continue
    output_md += f'### {section}\n\n'
    source_data = source_tables[section]
    headers = source_data[0]
    if 'Posting' not in headers:
        continue
    posting_idx = headers.index('Posting')
    rows = source_data[2:]  # skip headers and separator
    tracking_map = {}
    if section in tracking_tables:
        track_data = tracking_tables[section]
        track_headers = track_data[0]
        if 'Status' in track_headers and 'Posting' in track_headers:
            track_posting_idx = track_headers.index('Posting')
            for row in track_data[2:]:
                if len(row) == len(track_headers):
                    posting_url = get_url(row[track_posting_idx])
                    status = row[-1]
                    tracking_map[posting_url] = status
    new_headers = headers + ['Status']
    new_rows = []
    for row in rows:
        posting_cell = row[posting_idx]
        posting_url = get_url(posting_cell)
        status = tracking_map.get(posting_url, '- [ ]')
        new_rows.append(row + [status])
    output_md += generate_md_table(new_headers, new_rows)
    output_md += '\n'

with open('my-tracking.md', 'w', encoding='utf-8') as f:
    f.write(output_md)
