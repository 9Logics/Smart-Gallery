import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target = """#lightbox-filmstrip-container.hidden {
    opacity: 0;
    height: 0;"""

replacement = """#lightbox-filmstrip-container.hidden {
    display: flex !important;
    opacity: 0;
    height: 0;"""

if target in css:
    css = css.replace(target, replacement)
    print("Patched hidden class")
else:
    print("Target not found")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
