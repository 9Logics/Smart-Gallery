js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace("if (e.key === 'ArrowLeft') {", "if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') {")
js = js.replace("} else if (e.key === 'ArrowRight') {", "} else if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') {")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated keyboard bindings to include A/D")
