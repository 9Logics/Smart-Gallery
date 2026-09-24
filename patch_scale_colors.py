import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace palettes logic with single colors
old_palettes = '''    const palettes = [
        ['#0A2463', '#3E92CC', '#D8315B', '#1E1B18', '#FFFAFF'], // Classic Navy & Crimson
        ['#FF595E', '#FFCA3A', '#8AC926', '#1982C4', '#6A4C93'], // Modern Vibrant
        ['#22333B', '#EAE0D5', '#C6AC8F', '#5E503F', '#0A0908'], // Coffee/Sepia
        ['#006BA6', '#0496FF', '#FFBC42', '#D81159', '#8F2D56'], // Bold Pop
        ['#386641', '#6A994E', '#A3B18A', '#E2E8CE', '#BC4749'], // Nature Forest
        ['#540D6E', '#EE4266', '#FFD23F', '#3BCEAC', '#0EAD69']  // Neon Festival
    ];
    
    // Select palette
    const palette = palettes[Math.floor(myRand() * palettes.length)];'''

new_palettes = '''    // Pick ONE solid theme color for the entire year
    const themeColors = [
        '#FF0A54', // Crimson
        '#00BBF9', // Cyan
        '#FEE440', // Yellow
        '#00F5D4', // Mint
        '#9B5DE5', // Purple
        '#FA709A', // Pink
        '#8AC926', // Lime
        '#1982C4', // Blue
        '#FF595E'  // Coral
    ];
    const themeColor = themeColors[Math.floor(myRand() * themeColors.length)];'''

js = js.replace(old_palettes, new_palettes)

# Replace palette assignments with themeColor
js = js.replace('palette[i % palette.length]', 'themeColor')

# Fix Sizes
js = js.replace("const size = (200 + myRand() * 400) + 'px';", "const size = (60 + myRand() * 120) + 'px';")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

# Fix CSS sizes for goopy circles and morphing blobs
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Morphing Blob size
css = css.replace('width: 60vh;\n    height: 60vh;', 'width: 25vh;\n    height: 25vh;')

# Goopy circle (.theme-blob) size (it's probably 200px or something)
css = re.sub(
    r'\.theme-blob\s*\{[^}]*\}',
    '''.theme-blob {
    position: absolute;
    width: 15vh;
    height: 15vh;
    border-radius: 50%;
    animation: floatBlob 15s infinite alternate ease-in-out;
}''',
    css
)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("Scaled down shapes and locked to a single theme color per year!")
