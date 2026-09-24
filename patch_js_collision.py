import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace isTransitioning with isRecapTransitioning
js = js.replace('let isTransitioning = false;', 'let isRecapTransitioning = false;')
js = js.replace('if (isTransitioning) return;', 'if (isRecapTransitioning) return;')
js = js.replace('isTransitioning = true;', 'isRecapTransitioning = true;')
js = js.replace('isTransitioning = false;', 'isRecapTransitioning = false;')

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Fixed variable redeclaration error!")
