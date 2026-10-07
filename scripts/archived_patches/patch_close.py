path = 'app/static/style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

target = """.recap-close {
    position: absolute;
    top: 30px;
    right: 30px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    z-index: 10001;
    backdrop-filter: blur(10px);
}
.recap-close:hover {
    background: rgba(255,255,255,0.4);
}"""

replacement = """.recap-close {
    position: absolute;
    top: 30px;
    right: 30px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    z-index: 10001;
    backdrop-filter: blur(10px);
    transition: background 0.3s ease, transform 0.3s ease;
}
.recap-close:hover {
    background: rgba(255,255,255,0.4);
    transform: scale(1.1);
}
.recap-close:active {
    transform: scale(0.9);
}"""

if target in css:
    css = css.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Patched recap-close hover transition")
else:
    print("Could not find recap-close target")
