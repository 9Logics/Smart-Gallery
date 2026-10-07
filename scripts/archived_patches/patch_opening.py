import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Hide clone's text and buttons so they don't stretch uglily
js = js.replace("document.body.appendChild(clone);", "Array.from(clone.children).forEach(c => { c.style.transition='opacity 0.2s'; c.style.opacity='0'; });\n    document.body.appendChild(clone);")

# Fade out the clone instead of abrupt remove
js = js.replace("if (clone) clone.remove();", "if (clone) { clone.style.opacity = '0'; window.recapSetTimeout(() => clone.remove(), 600); }")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print('Optimized JS opening sequence')
