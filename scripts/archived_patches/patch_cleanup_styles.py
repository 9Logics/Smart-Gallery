import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_close = '''function closeRecapPlayer() {
    isRecapLoading = false;'''

new_close = '''function closeRecapPlayer() {
    isRecapLoading = false;
    document.querySelectorAll('.dynamic-float-style').forEach(el => el.remove());'''

js = js.replace(old_close, new_close)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated closeRecapPlayer for cleanup!")
