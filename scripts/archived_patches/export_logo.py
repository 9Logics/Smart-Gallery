import re
with open('app/templates/partials/sidebar.html', 'r', encoding='utf-8') as f:
    html = f.read()
m = re.search(r'<svg class="logo-icon"[^>]*>.*?</svg>', html, re.DOTALL)
if m:
    with open('test_logo.html', 'w', encoding='utf-8') as out:
        out.write(f"<html><body style='background: #111;'><div style='width: 44px; height: 44px;'>{m.group(0)}</div></body></html>")
    print("Exported to test_logo.html")
