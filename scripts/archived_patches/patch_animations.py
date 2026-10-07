import re
path = 'app/static/style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Restore background recession animation
target_bg = """body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .top-header {
    /* transform removed to fix lag on heavy DOMs */
    opacity: 0;
    pointer-events: none;
}"""

replacement_bg = """body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .top-header {
    transform: scale(0.92) translate3d(0, -30px, 0);
    opacity: 0;
    pointer-events: none;
}"""

css = css.replace(target_bg, replacement_bg)

# 2. Restore hover animation on mini cards
target_hover = """.rewind-mini-card:hover {
    /* Box transform removed to prevent cursor edge glitching, only the image inside will scale */
    box-shadow: 0 16px 32px rgba(0,0,0,0.6);
}"""

replacement_hover = """.rewind-mini-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 16px 32px rgba(0,0,0,0.6);
}"""

css = css.replace(target_hover, replacement_hover)

# 3. Restore hover animation on hero card (if it exists)
target_hero_hover = """.rewind-hero-card:hover {
    /* Box transform removed to prevent cursor edge glitching */
    box-shadow: 0 20px 50px rgba(0,0,0,0.7);
}"""

replacement_hero_hover = """.rewind-hero-card:hover {
    transform: translateY(-10px) scale(1.01);
    box-shadow: 0 20px 50px rgba(0,0,0,0.7);
}"""

if target_hero_hover in css:
    css = css.replace(target_hero_hover, replacement_hero_hover)
else:
    css += "\n.rewind-hero-card:hover { transform: translateY(-10px) scale(1.01); box-shadow: 0 20px 50px rgba(0,0,0,0.7); }"

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated style.css")
