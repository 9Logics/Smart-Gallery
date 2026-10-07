import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

target = '''.recap-nav-left, .recap-nav-right {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 30%;
    z-index: 10000;
    cursor: pointer;
}
.recap-nav-left { left: 0; }
.recap-nav-right { right: 0; }'''

replacement = '''.recap-bottom-controls {
    position: absolute;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 20px;
    z-index: 10001;
}

.recap-nav-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 28px;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 30px;
    color: white;
    font-size: 16px;
    font-weight: 600;
    font-family: 'Outfit', sans-serif;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: pointer;
    backdrop-filter: blur(15px);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.recap-nav-btn:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 15px 30px rgba(0,0,0,0.3);
}

.recap-nav-btn:active {
    transform: translateY(1px);
    box-shadow: 0 5px 10px rgba(0,0,0,0.2);
}'''

css = css.replace(target, replacement)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated CSS")
