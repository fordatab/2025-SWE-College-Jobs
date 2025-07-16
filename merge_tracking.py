import re

def extract_sections(md_content):
    lines = md_content.splitlines()
    sections = {}
    current_section = None
    section_data = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('### '):
            if current_section and section_data:
                sections[current_section] = section_data
            current_section = stripped[4:].strip()
            section_data = []
            in_section = False
        if stripped.startswith('|') and 'Posting' in stripped:
            headers = [c.strip() for c in line.split('|')[1:-1]]
            in_section = True
        elif in_section and stripped.startswith('|'):
            row = [c.strip() for c in line.split('|')[1:-1]]
            section_data.append(row)
    if current_section and section_data:
        sections[current_section] = section_data
    return sections, headers if 'headers' in locals() else []

def get_url(cell):
    match = re.search(r'\[\]\((https?://.*?)\)', cell)
    return match.group(1) if match else ''

with open('README.md', 'r', encoding='utf-8') as f:
    readme_content = f.read()

source_sections, source_headers = extract_sections(readme_content)

try:
    with open('my-tracking.md', 'r', encoding='utf-8') as f:
        tracking_content = f.read()
except FileNotFoundError:
    tracking_content = ''

tracking_map = {}
if tracking_content:
    lines = tracking_content.splitlines()
    for line in lines:
        match = re.match(r'^\s*-\s*\[([ x])\]\s*(.*)', line)
        if match:
            status_char = match.group(1)
            rest = match.group(2)
            url_match = re.search(r'\[\w*\]\((https?://[^)]+)\)', rest)
            if url_match:
                url = url_match.group(1)
                status = f' [{"x" if status_char == "x" else " "}] '
                tracking_map[url] = status

output_md = '# 2025 SWE College Jobs - My Tracking\n\n'
output_md += 'This file is automatically updated daily from README.md, preserving your application statuses. Check off applied jobs by clicking the checkboxes in a Markdown editor like VS Code with the "Markdown Interactive Checkbox" extension.\n\n'
output_md += '## 2025 USA SWE Internships 📚🦅\n\n'

sections_order = ['FAANG+', 'Quant', 'Other']
for section in sections_order:
    if section not in source_sections:
        continue
    output_md += f'### {section}\n\n'
    source_rows = source_sections[section]
    company_idx = source_headers.index('Company') if 'Company' in source_headers else 0
    role_idx = source_headers.index('Role') if 'Role' in source_headers else 1
    location_idx = source_headers.index('Location') if 'Location' in source_headers else 2
    posting_idx = source_headers.index('Posting') if 'Posting' in source_headers else 3
    for row in source_rows:
        if len(row) < 4:
            continue
        company = row[company_idx]
        role = row[role_idx]
        location = row[location_idx]
        posting = row[posting_idx]
        url = get_url(posting)
        if not url:
            continue
        status = tracking_map.get(url, '- [ ] ')
        line = f'{status}{company} | {role} | {location} | {posting}\n'
        output_md += line
    output_md += '\n'

with open('my-tracking.md', 'w', encoding='utf-8') as f:
    f.write(output_md)
