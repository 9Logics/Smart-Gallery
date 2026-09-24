import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Remove the old progress bar logic
js = js.replace("const progress = document.getElementById('recap-progress-fill');", "")
js = js.replace("progress.style.width = '0%';", "")
js = js.replace("progress.style.width = prog + '%';", "")
js = js.replace("progress.style.width = '100%';", "")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Removed old progress bar logic from recap_player.js")
