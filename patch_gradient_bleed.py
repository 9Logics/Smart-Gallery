import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_css = '''.window-ai-gradient {
    position: fixed; /* Fixed to viewport */'''
new_css = '''.window-ai-gradient {
    position: absolute; /* Absolute to the recap container so it doesn't bleed onto the main app */'''

if old_css in css:
    css = css.replace(old_css, new_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed position: fixed bug!")
else:
    print("Could not find old css!")

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('v=264', 'v=265')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
