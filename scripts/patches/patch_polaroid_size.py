import os
import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Make the first montage polaroids bigger
old_polaroid = '''
.montage-polaroid {
    position: absolute;
    width: 32vw;
    max-width: 360px;
    aspect-ratio: 4/5;
    background: #fff;
    padding: 12px 12px 50px 12px;'''

new_polaroid = '''
.montage-polaroid {
    position: absolute;
    width: 45vw;
    max-width: 550px;
    aspect-ratio: 4/5;
    background: #fff;
    padding: 16px 16px 65px 16px;'''

css = css.replace(old_polaroid, new_polaroid)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Made polaroids bigger!")
