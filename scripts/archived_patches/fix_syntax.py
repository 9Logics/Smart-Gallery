js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the second 'const overlay' with just 'overlay' or remove it
js = js.replace("const overlay = document.getElementById('recap-player-overlay');\n    const preloader =", "const preloader =")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Fixed duplicate overlay declaration")
