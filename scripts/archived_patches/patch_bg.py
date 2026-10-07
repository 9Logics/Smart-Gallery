import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """.main-content, .sidebar, .header-area {
    
}"""

replacement = """.main-content, .sidebar, .header-area {
    transition: all 0.8s cubic-bezier(0.785, 0.135, 0.15, 0.86);
}"""

css = css.replace(target, replacement)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated CSS with main content transition")
