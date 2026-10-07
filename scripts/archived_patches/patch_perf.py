import re
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .header-area {
    transform: scale(0.9) translateY(-40px);
    filter: blur(15px);
    opacity: 0;
    pointer-events: none;
}

.main-content, .sidebar, .top-header {
    transition: all 0.8s cubic-bezier(0.785, 0.135, 0.15, 0.86);
}"""

replacement = """body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .top-header {
    transform: scale(0.9) translate3d(0, -40px, 0);
    opacity: 0;
    pointer-events: none;
}

.main-content, .sidebar, .top-header {
    transition: transform 0.8s cubic-bezier(0.785, 0.135, 0.15, 0.86), opacity 0.6s cubic-bezier(0.785, 0.135, 0.15, 0.86);
    will-change: transform, opacity;
}"""

css = css.replace(target, replacement)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated CSS to remove blur and optimize performance")
