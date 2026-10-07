import re
with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()
css = re.sub(r'(\.logo-icon \.a\s*\{\s*)fill:\s*var\(--accent-color\);', r'\1fill: rgba(255, 255, 255, 0.4);\n    filter: brightness(0.65);', css)
with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Restored logo fill")
