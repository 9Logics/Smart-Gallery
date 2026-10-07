import re
with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = re.sub(r'(\.sidebar-header\s*\{[^}]*?)height:\s*32px;([^}]*?\})', r'\1/* height: 32px; removed to prevent squishing */\2', css)

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Removed height constraint on sidebar-header")
