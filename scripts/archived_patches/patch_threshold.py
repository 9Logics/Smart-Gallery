import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

target = """    const validRunners = runnersUp.filter(r => r.cover_face_id && r.name && !r.name.startsWith('Unnamed') && !r.name.startsWith('Person '));
    if (validRunners.length < 2) {"""

replacement = """    const validRunners = runnersUp.filter(r => r.cover_face_id && r.name && !r.name.startsWith('Unnamed') && !r.name.startsWith('Person '));
    if (validRunners.length < 1) {"""

js = js.replace(target, replacement)
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated validRunners threshold")
