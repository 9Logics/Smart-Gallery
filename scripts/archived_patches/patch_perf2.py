import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """    overflow: hidden;
    transition: transform 0.8s cubic-bezier(0.785, 0.135, 0.15, 0.86);
}

body.recap-active .recap-container {
    transform: translateY(-100vh);
}"""

replacement = """    overflow: hidden;
    transition: transform 0.8s cubic-bezier(0.785, 0.135, 0.15, 0.86);
    will-change: transform;
}

body.recap-active .recap-container {
    transform: translate3d(0, -100vh, 0);
}"""

css = css.replace(target, replacement)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated recap-container performance")
