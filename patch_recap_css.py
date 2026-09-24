import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

recap_player_css = '''
/* RECAP PLAYER OVERLAY */
#recap-player-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: #000;
    color: white;
    font-family: system-ui, -apple-system, sans-serif;
    overflow: hidden;
}

#recap-player-overlay.hidden {
    display: none;
}

/* Skiper 30 Parallax Backdrop */
.recap-backdrop {
    position: absolute;
    inset: -10%;
    width: 120%;
    height: 120%;
    background-size: cover;
    background-position: center;
    filter: blur(20px) brightness(0.3);
    animation: panBackdrop 20s linear infinite alternate;
}

@keyframes panBackdrop {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-5%, -5%) scale(1.1); }
}

/* Skiper 15 Preloader */
.recap-preloader-screen {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #000;
    z-index: 10000;
    transition: transform 1s cubic-bezier(0.785, 0.135, 0.15, 0.86);
}

.recap-preloader-screen.slide-up {
    transform: translateY(-100%);
}

.preloader-text {
    font-size: 24px;
    font-weight: 600;
    letter-spacing: 2px;
    margin-bottom: 20px;
    text-transform: uppercase;
    background: linear-gradient(90deg, #fff, #888);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.preloader-progress-bar {
    width: 200px;
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    overflow: hidden;
}

#recap-progress-fill {
    width: 0%;
    height: 100%;
    background: white;
    transition: width 0.3s ease;
}

/* Slides */
#recap-slides-container {
    position: absolute;
    inset: 0;
    display: flex;
    z-index: 9999;
}

.recap-slide {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.8s ease, transform 0.8s ease;
    transform: scale(0.95);
    text-align: center;
    padding: 40px;
}

.recap-slide.active {
    opacity: 1;
    pointer-events: auto;
    transform: scale(1);
}

.recap-slide h1 {
    font-size: 48px;
    font-weight: 800;
    margin: 20px 0;
    line-height: 1.2;
    text-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.recap-slide h2 {
    font-size: 24px;
    font-weight: 500;
    color: rgba(255,255,255,0.7);
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Skiper 37 Number Stats */
.recap-stat-number {
    font-size: 80px;
    font-weight: 900;
    background: linear-gradient(135deg, #0A84FF, #FF0A54);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 10px 20px rgba(0,0,0,0.5));
}

.highlight-text {
    background: linear-gradient(135deg, #32D74B, #0A84FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Iconic Place Card */
.iconic-place-card {
    position: relative;
    width: 300px;
    height: 400px;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 30px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}

.iconic-place-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.iconic-place-card h1 {
    position: absolute;
    bottom: 20px;
    left: 20px;
    right: 20px;
    font-size: 32px;
    margin: 0;
    z-index: 2;
}

.sticker-animated {
    position: absolute;
    top: -20px;
    right: -20px;
    font-size: 60px;
    filter: drop-shadow(0 10px 10px rgba(0,0,0,0.5));
    animation: stickerBounce 2s cubic-bezier(0.175, 0.885, 0.32, 1.275) infinite alternate;
    z-index: 10;
}

@keyframes stickerBounce {
    0% { transform: scale(1) rotate(-10deg); }
    100% { transform: scale(1.2) rotate(10deg); }
}

/* Navigation */
.recap-nav-left, .recap-nav-right {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 30%;
    z-index: 10000;
    cursor: pointer;
}
.recap-nav-left { left: 0; }
.recap-nav-right { right: 0; }

.recap-close {
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
}

/* FLIP Transition Clone */
.recap-transition-clone {
    position: fixed;
    z-index: 100000;
    transition: all 0.6s cubic-bezier(0.785, 0.135, 0.15, 0.86);
    object-fit: cover;
    pointer-events: none;
}
'''

if '/* RECAP PLAYER OVERLAY */' not in css:
    css += '\n' + recap_player_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added recap player CSS!")
else:
    print("CSS already exists.")
