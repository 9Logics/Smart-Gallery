import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix logo-text
css = css.replace(
    '''.logo-text {
    font-family: var(--font-display);
    font-size: 24px;
    font-weight: 800;
    background: var(--accent-gradient);
    
    
}''',
    '''.logo-text {
    font-family: var(--font-display);
    font-size: 24px;
    font-weight: 800;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}'''
)

# Fix roll-char
css = css.replace(
    '''.rolling-text-title .roll-char {
    background: #ffffff;
    
    
}''',
    '''.rolling-text-title .roll-char {
    color: #ffffff;
    background: transparent;
}'''
)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed text background-clip bugs!")
