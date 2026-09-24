import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

professional_css = '''
/* Professional Design Engineering Utilities */
button:active, .recap-trigger:active, .rewind-hero-card:active, .rewind-mini-card:active {
    transform: scale(0.97);
    transition: transform 160ms cubic-bezier(0.23, 1, 0.32, 1);
}

button, .recap-trigger, .rewind-hero-card, .rewind-mini-card {
    transition: transform 200ms cubic-bezier(0.23, 1, 0.32, 1), opacity 200ms cubic-bezier(0.23, 1, 0.32, 1);
    will-change: transform;
}
'''

if '/* Professional Design Engineering Utilities */' not in css:
    css += '\n' + professional_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added professional click feedback scales!")
else:
    print("Already added.")
