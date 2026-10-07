import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Hide the scrollbar entirely
target = """#lightbox-filmstrip-container::-webkit-scrollbar {
    height: 6px;
}"""
replacement = """#lightbox-filmstrip-container::-webkit-scrollbar {
    display: none;
}"""
css = css.replace(target, replacement)

# 2. Fix the height and spacing of the filmstrip container
# Currently it's height: 85px; padding: 10px 24px;
# Let's change it to height: 80px; padding: 10px 16px; 
target2 = """#lightbox-filmstrip-container {
    width: calc(100% - 48px);
    height: 85px;
    margin: 0 auto 24px auto;"""
replacement2 = """#lightbox-filmstrip-container {
    width: max-content;
    max-width: calc(100% - 48px);
    height: 80px;
    margin: 0 auto 24px auto;"""
css = css.replace(target2, replacement2)

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
