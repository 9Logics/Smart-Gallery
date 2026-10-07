import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Use regex to replace the entire skiper19-line-container block
pattern = r'<div class="skiper19-line-container">.*?</div>'
replacement = '''<div class="m3-expressive-shapes">
                <div class="m3-shape shape-1"></div>
                <div class="m3-shape shape-2"></div>
            </div>'''

new_html = re.sub(pattern, replacement, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Replaced skiper19 with m3-expressive-shapes")
