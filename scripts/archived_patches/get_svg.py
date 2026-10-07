import re
with open('app/templates/partials/sidebar.html', 'r', encoding='utf-8') as f:
    html = f.read()
m = re.search(r'<svg class="logo-icon"[^>]*>.*?</svg>', html, re.DOTALL)
if m:
    print(m.group(0)[:500])
else:
    print("No SVG found")
