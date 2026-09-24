import os
import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix the roll-char-wrap clipping with even larger em values to prevent any descender cutoff
css = css.replace('padding-bottom: 0.2em;', 'padding-bottom: 0.4em;')
css = css.replace('margin-bottom: -0.2em;', 'margin-bottom: -0.4em;')
css = css.replace('padding-top: 0.1em;', 'padding-top: 0.3em;')
css = css.replace('margin-top: -0.1em;', 'margin-top: -0.3em;')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("Safeguarded roll-char-wrap clipping!")
