import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update recap-glow
old_glow = 'background: radial-gradient(ellipse at bottom, rgba(150, 50, 255, 0.6) 0%, transparent 70%);'
new_glow = 'background: radial-gradient(ellipse at bottom, rgba(10, 132, 255, 0.6) 0%, transparent 70%);'
if old_glow in css:
    css = css.replace(old_glow, new_glow)
    print("Fixed recap-glow!")
else:
    print("Could not find old_glow!")

# 2. Update recap-container background
old_bg = 'background: radial-gradient(circle at center, #1a1a2e 0%, #050505 100%);'
new_bg = 'background: radial-gradient(circle at center, #051525 0%, #050505 100%);'
if old_bg in css:
    css = css.replace(old_bg, new_bg)
    print("Fixed recap-container bg!")
else:
    print("Could not find old_bg!")

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
