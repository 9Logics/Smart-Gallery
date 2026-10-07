import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

new_css = '''
/* Scrapbook Montage Transition Buffer */
#montage-container {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.montage-polaroid {
    position: absolute;
    width: 32vw;
    max-width: 360px;
    aspect-ratio: 4/5;
    background: #fff;
    padding: 12px 12px 50px 12px;
    border-radius: 6px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,0,0,0.1) inset;
    opacity: 0;
    transform: scale(1.8) translateY(-100px);
    transition: transform 0.6s cubic-bezier(0.2, 1.2, 0.4, 1), opacity 0.4s ease-out;
    will-change: transform, opacity;
}

.montage-polaroid.in {
    opacity: 1;
    /* Transform set inline by JS */
}

.montage-polaroid.out {
    transform: scale(0.8) translateY(200px) rotate(10deg) !important;
    opacity: 0 !important;
    transition: transform 0.5s cubic-bezier(0.8, 0, 0.2, 1), opacity 0.4s ease-in;
}

.montage-polaroid img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 3px;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
}
'''

if 'Scrapbook Montage Transition Buffer' not in css:
    css += new_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added montage CSS!")
