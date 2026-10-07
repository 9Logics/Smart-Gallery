import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target = """.lightbox-sidebar {
    width: 380px;
    background: rgba(15, 22, 38, 0.85); /* Deep premium translucent blue */
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding: 32px 28px;
    z-index: 1000;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1);
    
    /* Floating positioning */"""

replacement = """.lightbox-sidebar {
    width: 380px;
    background: rgba(15, 22, 38, 0.85); /* Deep premium translucent blue */
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 1000;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1);
    
    /* Floating positioning */"""

if target in css:
    css = css.replace(target, replacement)
    print("Replaced CSS")
else:
    print("CSS Target not found")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
