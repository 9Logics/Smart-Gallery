import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the debugger script I injected
html = re.sub(r'<script>\s*document\.addEventListener\(\'click\', function\(e\).*?console\.log\(\'recap-close 2:\', rect2\);\s*\}, 2000\);\s*</script>', '', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Removed debug script")
