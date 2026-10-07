css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace('.recap-preloader-screen {\n    position: absolute;\n    inset: 0;', '.recap-preloader-screen {\n    position: absolute;\n    inset: 0;\n    z-index: 100;')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated preloader z-index")
