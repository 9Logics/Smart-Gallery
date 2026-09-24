import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix Hero Card Hover Glitch
old_hero_hover = '''.rewind-hero-card:hover {
    transform: scale(1.01);
}'''
new_hero_hover = '''.rewind-hero-card:hover {
    /* Box transform removed to prevent cursor edge glitching */
}'''
if old_hero_hover in css:
    css = css.replace(old_hero_hover, new_hero_hover)
    print("Fixed hero hover!")
else:
    print("Could not find hero hover!")

# Fix Mini Card Hover Glitch
old_mini_hover = '''.rewind-mini-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 16px 32px rgba(0,0,0,0.6);
}'''
new_mini_hover = '''.rewind-mini-card:hover {
    /* Box transform removed to prevent cursor edge glitching, only the image inside will scale */
    box-shadow: 0 16px 32px rgba(0,0,0,0.6);
}'''
if old_mini_hover in css:
    css = css.replace(old_mini_hover, new_mini_hover)
    print("Fixed mini card hover!")
else:
    print("Could not find mini card hover!")

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=271', 'v=272')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
