import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Tone down the parallax
js = js.replace('(window.innerWidth / 2 - e.pageX) / 25', '(window.innerWidth / 2 - e.pageX) / 80')
js = js.replace('(window.innerHeight / 2 - e.pageY) / 25', '(window.innerHeight / 2 - e.pageY) / 80')
js = js.replace('(depth / 1000)', '(depth / 3000)')

# 2. Fix the palettes (monochromatic & cohesive instead of mixed pastels)
old_palettes = '''    const palettes = [
        ['#FF0A54', '#FF477E', '#FF7096', '#FF85A1', '#FBB1BD'], // Pink Goo
        ['#00F5D4', '#00BBF9', '#FEE440', '#F15BB5', '#9B5DE5'], // Retro Pop
        ['#FF9A9E', '#FECFEF', '#A1C4FD', '#C2E9FB', '#D4FC79'], // Dreamy Pastel
        ['#FA709A', '#FEE140', '#F3A183', '#556270', '#FF3CAC'], // Sunset Paint
        ['#8EC5FC', '#E0C3FC', '#4FACFE', '#00F2FE', '#38F9D7'], // Frosty Fluid
        ['#ff0055', '#0033ff', '#00ff99', '#ffff00', '#ff00ff']  // Cyber Neon
    ];'''

new_palettes = '''    const palettes = [
        ['#0A2463', '#3E92CC', '#D8315B', '#1E1B18', '#FFFAFF'], // Classic Navy & Crimson
        ['#FF595E', '#FFCA3A', '#8AC926', '#1982C4', '#6A4C93'], // Modern Vibrant
        ['#22333B', '#EAE0D5', '#C6AC8F', '#5E503F', '#0A0908'], // Coffee/Sepia
        ['#006BA6', '#0496FF', '#FFBC42', '#D81159', '#8F2D56'], // Bold Pop
        ['#386641', '#6A994E', '#A3B18A', '#E2E8CE', '#BC4749'], // Nature Forest
        ['#540D6E', '#EE4266', '#FFD23F', '#3BCEAC', '#0EAD69']  // Neon Festival
    ];'''
    
js = js.replace(old_palettes, new_palettes)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Toned down parallax and updated themes!")
