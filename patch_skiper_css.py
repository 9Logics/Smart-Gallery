import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Remove gradients on texts
css = css.replace('background: linear-gradient(135deg, #0A84FF, #FF0A54);', 'color: white;')
css = css.replace('-webkit-background-clip: text;', '')
css = css.replace('-webkit-text-fill-color: transparent;', '')
css = css.replace('background: linear-gradient(135deg, #32D74B, #0A84FF);', 'color: #C2F84F;')
css = css.replace('background: linear-gradient(90deg, #fff, #888);', 'color: white;')

# 2. Add Skiper15 3D Box Preloader CSS
skiper15_css = '''
/* Skiper15 3D Box Preloader */
.box-preloader-container {
    perspective: 1000px;
    margin-bottom: 40px;
}
.box-3d {
    width: 60px;
    height: 60px;
    position: relative;
    transform-style: preserve-3d;
    animation: rotateBox3D 2s infinite cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.box-face {
    position: absolute;
    width: 60px;
    height: 60px;
    background: rgba(255,255,255,0.1);
    border: 2px solid white;
    box-shadow: inset 0 0 20px rgba(255,255,255,0.2);
}
.box-face.front  { transform: translateZ(30px); }
.box-face.back   { transform: rotateY(180deg) translateZ(30px); }
.box-face.right  { transform: rotateY(90deg) translateZ(30px); }
.box-face.left   { transform: rotateY(-90deg) translateZ(30px); }
.box-face.top    { transform: rotateX(90deg) translateZ(30px); }
.box-face.bottom { transform: rotateX(-90deg) translateZ(30px); }

@keyframes rotateBox3D {
    0% { transform: rotateX(0deg) rotateY(0deg); }
    50% { transform: rotateX(180deg) rotateY(90deg); }
    100% { transform: rotateX(360deg) rotateY(360deg); }
}
'''

# 3. Add Skiper30 Parallax Gallery CSS
skiper30_css = '''
/* Skiper30 Parallax Gallery */
.parallax-gallery-container {
    position: absolute;
    inset: -20%;
    width: 140%;
    height: 140%;
    z-index: 0;
    pointer-events: none;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-around;
}
.parallax-gallery-item {
    position: absolute;
    border-radius: 12px;
    object-fit: cover;
    box-shadow: 0 30px 60px rgba(0,0,0,0.6);
    opacity: 0.4;
    transition: transform 0.2s ease-out;
}
/* Individual floating animations for items */
.p-item-1 { width: 300px; height: 400px; top: 10%; left: 10%; animation: floatP1 25s infinite alternate ease-in-out; }
.p-item-2 { width: 200px; height: 200px; top: 60%; left: 15%; animation: floatP2 20s infinite alternate ease-in-out; }
.p-item-3 { width: 400px; height: 250px; top: 20%; right: 10%; animation: floatP3 30s infinite alternate ease-in-out; }
.p-item-4 { width: 250px; height: 350px; bottom: 10%; right: 20%; animation: floatP4 22s infinite alternate ease-in-out; }
.p-item-5 { width: 350px; height: 350px; top: 40%; left: 40%; animation: floatP5 28s infinite alternate ease-in-out; }

@keyframes floatP1 { 0% { transform: translateY(0) rotate(-5deg); } 100% { transform: translateY(100px) rotate(5deg); } }
@keyframes floatP2 { 0% { transform: translateY(0) rotate(10deg); } 100% { transform: translateY(-80px) rotate(-10deg); } }
@keyframes floatP3 { 0% { transform: translateY(0) rotate(-2deg); } 100% { transform: translateY(120px) rotate(8deg); } }
@keyframes floatP4 { 0% { transform: translateY(0) rotate(5deg); } 100% { transform: translateY(-150px) rotate(-5deg); } }
@keyframes floatP5 { 0% { transform: translateY(0) rotate(-8deg); } 100% { transform: translateY(80px) rotate(2deg); } }
'''

# 4. Add Skiper37 Number Flow Slot Machine CSS
skiper37_css = '''
/* Skiper37 Animated Number Flow */
.number-flow-wrapper {
    display: inline-flex;
    height: 100px;
    overflow: hidden;
    line-height: 100px;
    font-size: 100px;
    font-weight: 900;
    color: white;
}
.number-flow-digit {
    display: inline-flex;
    flex-direction: column;
    transition: transform 2.5s cubic-bezier(0.2, 0.8, 0.2, 1);
}
'''

# 5. Skiper19 LinePath SVG
skiper19_css = '''
/* Skiper19 LinePath */
.skiper19-line-container {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: -1;
}
.skiper19-path {
    stroke-dasharray: 4000;
    stroke-dashoffset: 4000;
    animation: drawLinePath 4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
@keyframes drawLinePath {
    to { stroke-dashoffset: 0; }
}
'''

# 6. Skiper29 Siena Parallax Depth
skiper29_css = '''
/* Skiper29 Siena Depth */
.recap-slide.siena-depth {
    transform-style: preserve-3d;
    perspective: 1000px;
}
.siena-layer {
    transition: transform 0.1s ease-out;
}
'''

if '/* Skiper15 3D Box Preloader */' not in css:
    css += '\n' + skiper15_css + '\n' + skiper30_css + '\n' + skiper37_css + '\n' + skiper19_css + '\n' + skiper29_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Injected Skiper CSS features!")
else:
    print("Skiper CSS already exists!")
