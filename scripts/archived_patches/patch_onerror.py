import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = "document.body.appendChild(errorDiv);"
replacement = "if (document.body) { document.body.appendChild(errorDiv); } else { document.documentElement.appendChild(errorDiv); }"

if target in html:
    html = html.replace(target, replacement)
    with open('app/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Patched window.onerror in index.html")
else:
    print("Target not found in index.html")
