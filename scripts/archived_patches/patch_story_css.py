import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target = """.story-grid-bottom-btn {
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.2);"""

replacement = """.story-grid-bottom-btn {
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.2);
    pointer-events: auto; /* Required since it sits in pointer-events: none UI layer */"""

if target in css:
    css = css.replace(target, replacement)
    print("CSS updated with pointer-events: auto")
else:
    print("CSS target not found!")

# Also remove the idle rule if we want to clean it up
css = css.replace(".story-card-overlays.idle .story-grid-bottom-btn,", "")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
