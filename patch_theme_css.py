import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

theme_css = '''
/* Dynamic Themes */
#theme-canvas {
    position: absolute;
    inset: 0;
    overflow: hidden;
    z-index: 1; /* Above backdrop, below slides */
    opacity: 0.6;
    pointer-events: none;
}

.theme-blob {
    position: absolute;
    width: 60vh;
    height: 60vh;
    border-radius: 50%;
    animation: floatBlob 15s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
    mix-blend-mode: screen;
}

.theme-sharp {
    position: absolute;
    background-size: cover;
    animation: spinConfetti 10s infinite linear;
    opacity: 0.8;
}

.theme-orb {
    position: absolute;
    width: 80vh;
    height: 80vh;
    border-radius: 50%;
    animation: moveOrb 20s infinite alternate ease-in-out;
}

@keyframes floatBlob {
    0% { transform: translate(0, 0) scale(1) rotate(0deg); }
    33% { transform: translate(20vw, 30vh) scale(1.2) rotate(90deg); }
    66% { transform: translate(-20vw, 10vh) scale(0.8) rotate(180deg); }
    100% { transform: translate(10vw, -20vh) scale(1.1) rotate(270deg); }
}

@keyframes spinConfetti {
    0% { transform: translateY(-20vh) rotate(0deg); opacity: 1; }
    80% { opacity: 1; }
    100% { transform: translateY(120vh) rotate(720deg); opacity: 0; }
}

@keyframes moveOrb {
    0% { transform: translate(-20vw, -20vh); }
    100% { transform: translate(100vw, 100vh); }
}
'''

if '/* Dynamic Themes */' not in css:
    css += '\n' + theme_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added theme CSS!")
else:
    print("Theme CSS already exists.")
