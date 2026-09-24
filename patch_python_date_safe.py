import os

py_path = 'app/app_core.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

old_logic = '''    if results:
        return results
    day_month_regex = re.match('^(\\d{1,2})(?:st|nd|rd|th)?\\s*([a-z]+)$',
        query)'''

new_logic = '''    if results:
        return results
    
    # Handle Month YYYY (e.g. "August 2026")
    month_year_regex = re.match('^([a-z]+)\\s+(\\d{4})$', query)
    if month_year_regex:
        m_str, y_str = month_year_regex.groups()
        for i, m in enumerate(months):
            if m.startswith(m_str):
                results.append({'month': f'{i + 1:02d}', 'year': y_str})
                return results

    day_month_regex = re.match('^(\\d{1,2})(?:st|nd|rd|th)?\\s*([a-z]+)$',
        query)'''

if old_logic in py:
    py = py.replace(old_logic, new_logic)
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(py)
    print("Fixed parse_smart_dates in app_core!")
else:
    print("Could not find logic to replace!")
