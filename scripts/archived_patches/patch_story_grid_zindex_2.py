import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target = """.story-grid-view {
    position: absolute;
    inset: 0;
    background: var(--bg-color);
    z-index: 300;"""

replacement = """.story-grid-view {
    position: fixed;
    inset: 0;
    background: var(--bg-color);
    z-index: 450;"""

if target in css:
    css = css.replace(target, replacement)
    print("CSS z-index and position updated!")
else:
    print("CSS target not found!")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
