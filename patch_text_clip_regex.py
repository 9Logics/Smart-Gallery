import os
import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Fix .logo-text
css = re.sub(
    r'\.logo-text\s*\{[^}]*\}',
    '''.logo-text {
    font-family: var(--font-display);
    font-size: 24px;
    font-weight: 800;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}''',
    css
)

# 2. Fix .rolling-text-title .roll-char
css = re.sub(
    r'\.rolling-text-title \.roll-char\s*\{[^}]*\}',
    '''.rolling-text-title .roll-char {
    color: #ffffff;
    background: transparent;
}''',
    css
)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed text background-clip bugs via regex!")
