import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

scrapbook_css = '''
/* --- Scrapbook Typography & Aesthetics --- */

#recap-ai-comment {
    font-family: 'Pacifico', cursive;
    font-size: 3.5rem !important;
    line-height: 1.5;
    color: #fff;
    text-shadow: 3px 3px 0px rgba(0,0,0,0.4);
    transform: rotate(-3deg);
    padding: 30px 40px;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 3px dashed rgba(255, 255, 255, 0.4);
    border-radius: 15px;
    max-width: 80%;
    margin: 0 auto;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.recap-slide h2 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4.5rem !important;
    letter-spacing: 3px;
    transform: rotate(2deg);
    text-transform: uppercase;
    text-shadow: 4px 4px 0px rgba(0,0,0,0.6);
    margin-bottom: 15px;
    color: #f8f9fa;
}

/* Chunky Y2K Numbers */
.number-flow-wrapper {
    font-family: 'Titan One', display !important;
    color: #FFD23F !important;
    text-shadow: 4px 4px 0px #D8315B !important;
}

/* Cutout Paper Labels */
#recap-stat-person, #recap-stat-place {
    font-family: 'Righteous', display;
    font-size: 4rem !important;
    background: #00BBF9;
    color: #fff;
    padding: 10px 40px;
    border-radius: 4px;
    transform: rotate(-3deg) scale(1.1);
    box-shadow: 8px 8px 0px #0A2463;
    display: inline-block;
    margin-top: 25px;
    border: 2px solid #fff;
}
#recap-stat-person {
    background: #FF595E;
    box-shadow: 8px 8px 0px #540D6E;
    transform: rotate(2deg) scale(1.1);
}
'''

if 'Scrapbook Typography & Aesthetics' not in css:
    css += scrapbook_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added scrapbook typography CSS!")
