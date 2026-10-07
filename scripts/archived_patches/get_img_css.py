import re
with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

m = re.search(r'(\.photo-thumbnail\s*\{[^}]*?\})', css)
if m: print(m.group(1))

m2 = re.search(r'(\.photo-card img\s*\{[^}]*?\})', css)
if m2: print(m2.group(1))
