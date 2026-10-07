import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace('.main-content, .sidebar, .header-area', '.main-content, .sidebar, .top-header')
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed header class name")
