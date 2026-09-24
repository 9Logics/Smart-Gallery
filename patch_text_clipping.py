import os
import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix the roll-char-wrap clipping
old_wrap = '''.roll-char-wrap {
    display: inline-block;
    overflow: hidden;
    vertical-align: top;
    padding-bottom: 20px;
    margin-bottom: -20px;
    padding-right: 10px; /* Prevent right edge cutoff for italic/wide fonts */
    margin-right: -10px;
}'''

new_wrap = '''.roll-char-wrap {
    display: inline-block;
    overflow: hidden;
    vertical-align: bottom;
    padding-bottom: 0.2em; 
    margin-bottom: -0.2em;
    padding-top: 0.1em;
    margin-top: -0.1em;
    line-height: 1.2;
}'''

css = css.replace(old_wrap, new_wrap)

# Also ensure rolling-text-title has proper line-height
if 'line-height:' not in css.split('.rolling-text-title {')[1].split('}')[0]:
    css = css.replace('.rolling-text-title {\n    font-size: 6rem;', '.rolling-text-title {\n    line-height: 1.2;\n    font-size: 6rem;')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("Fixed roll-char-wrap clipping!")
