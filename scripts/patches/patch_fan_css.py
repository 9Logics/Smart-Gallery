import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

fan_css = '''
/* --- Fanned Polaroid Showcase --- */
#place-photos-fan {
    position: relative;
    width: 350px;
    height: 420px;
    margin: 30px auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.place-fan-photo {
    position: absolute;
    width: 280px;
    height: 350px;
    background: #fff;
    padding: 12px 12px 50px 12px;
    border-radius: 6px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,0,0,0.1) inset;
    transition: transform 0.6s cubic-bezier(0.2, 1.2, 0.4, 1);
    transform-origin: bottom center;
}

.place-fan-photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 3px;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
}
'''

if 'Fanned Polaroid Showcase' not in css:
    css += fan_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added fan CSS!")
