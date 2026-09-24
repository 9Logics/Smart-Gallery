import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_text_css = '''.rolling-text-title {
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

new_text_css = '''.rolling-text-title {
    font-size: 6rem;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    text-transform: uppercase;
    letter-spacing: -0.04em;
    filter: drop-shadow(0px 8px 24px rgba(255, 255, 255, 0.2));
    margin: 0;
    display: flex;
}
.rolling-text-title .roll-char {
    background: #ffffff;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}'''

if old_text_css in css:
    css = css.replace(old_text_css, new_text_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed CSS typography!")
else:
    print("Could not find old text css!")
