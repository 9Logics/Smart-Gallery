import os

py_path = 'app/app_core.py'
with open(py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if "day_month_regex = re.match('^" in line and "st|nd|rd|th" in line:
        # We found the line where day_month_regex starts.
        # Insert our month_year logic right before it!
        # Actually wait, we already appended `line` which is `day_month_regex = ...`. 
        # So we should insert BEFORE we append `line`.
        pass

# Let's do it cleaner
new_lines = []
for line in lines:
    if "day_month_regex = re.match('^" in line and "st|nd|rd|th" in line:
        new_lines.append("    month_year_regex = re.match('^([a-z]+)\\\\s+(\\\\d{4})$', query)\n")
        new_lines.append("    if month_year_regex:\n")
        new_lines.append("        m_str, y_str = month_year_regex.groups()\n")
        new_lines.append("        for i, m in enumerate(months):\n")
        new_lines.append("            if m.startswith(m_str):\n")
        new_lines.append("                results.append({'month': f'{i + 1:02d}', 'year': y_str})\n")
        new_lines.append("                return results\n")
    new_lines.append(line)

with open(py_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Safely patched parse_smart_dates!")
