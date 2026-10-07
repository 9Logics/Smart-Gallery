js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("clone.style.zIndex = '0';", "clone.style.zIndex = '10';")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated clone z-index")
