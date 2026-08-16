import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

def repl(m):
    prefix = m.group(1)
    return prefix + 'scan_status[\"status\"] = \"scanning\"\n' + prefix + 'scan_status[\"cancel_requested\"] = False'

new_text = re.sub(r'(^[ \t]*)scan_status\[\"status\"\] = \"scanning\"', repl, text, flags=re.MULTILINE)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_text)
print('Done!')
