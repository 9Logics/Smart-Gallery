import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Restore recap-close
recap_close_css = '''
.recap-close {
    position: absolute;
    top: 20px;
    right: 20px;
    cursor: pointer;
    opacity: 0.5;
    transition: opacity 0.3s;
    z-index: 99999;
}

.recap-close:hover {
    opacity: 1;
}
'''
if '.recap-close {' not in css:
    css += recap_close_css

# 2. Fix the rolling-text-title background clip
old_text_css = '''.rolling-text-title {
    font-size: 5rem;
    font-weight: 400;
    font-family: 'Abril Fatface', serif; /* Or var(--font-display) */
    background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 4px 15px rgba(255, 255, 255, 0.2));
    margin: 0;
    display: flex;
}'''

new_text_css = '''.rolling-text-title {
    font-size: 5rem;
    font-weight: 400;
    font-family: 'Abril Fatface', serif;
    filter: drop-shadow(0px 4px 15px rgba(255, 255, 255, 0.2));
    margin: 0;
    display: flex;
}
.rolling-text-title .roll-char {
    background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}'''

if old_text_css in css:
    css = css.replace(old_text_css, new_text_css)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed CSS!")
