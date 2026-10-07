path = 'app/static/style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Fix recap-container transition
target1 = """.recap-container {
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

replacement1 = """.recap-container {
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
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.8s ease;
}
body.recap-active .recap-trigger {
    opacity: 0 !important;
    transform: translateX(-50%) translateY(20px) !important;
    pointer-events: none;
}"""

css = css.replace(target1, replacement1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Patched style.css")
