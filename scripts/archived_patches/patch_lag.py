import re
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .top-header {
    transform: scale(0.9) translate3d(0, -40px, 0);
    opacity: 0;
    pointer-events: none;
}"""

replacement = """body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .top-header {
    /* transform removed to fix lag on heavy DOMs */
    opacity: 0;
    pointer-events: none;
}"""

css = css.replace(target, replacement)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated CSS to remove scale transform")
