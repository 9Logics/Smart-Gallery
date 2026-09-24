import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix the recap-trigger translation loss on active
css = css.replace(
    '''button:active, .recap-trigger:active, .rewind-hero-card:active, .rewind-mini-card:active {
    transform: scale(0.97);''',
    '''button:active, .recap-trigger:active, .rewind-hero-card:active, .rewind-mini-card:active {
    transform: scale(0.97);
}
.recap-trigger:active {
    transform: translateX(-50%) scale(0.97) !important;'''
)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed recap-trigger shift!")
