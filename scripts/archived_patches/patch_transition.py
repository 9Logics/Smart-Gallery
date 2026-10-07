import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """.recap-container {
    position: fixed;
    top: 100vh; /* Start below screen */
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at center, #051525 0%, #050505 100%);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    
    color: white;
    overflow: hidden;
}"""

replacement = """.recap-container {
    position: fixed;
    top: 100vh; /* Start below screen */
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at center, #051525 0%, #050505 100%);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    overflow: hidden;
    transition: transform 0.8s cubic-bezier(0.785, 0.135, 0.15, 0.86);
}"""

css = css.replace(target, replacement)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated CSS with transition")
