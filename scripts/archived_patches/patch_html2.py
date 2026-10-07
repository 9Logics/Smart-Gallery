path = 'app/templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('top: -10px; right: 20px;', 'top: 20px; right: 20px;')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed BETA marker position")
