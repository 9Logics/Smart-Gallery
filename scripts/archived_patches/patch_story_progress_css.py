import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target = """.story-progress-container {
    display: flex;
    gap: 4px;
    flex: 1;
}"""

replacement = """.story-progress-container {
    display: flex;
    gap: 4px;
    padding: 24px 24px 16px;
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 100;
    background: linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 100%);
}"""

if target in css:
    css = css.replace(target, replacement)
    print("CSS updated!")
else:
    print("CSS target not found!")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
