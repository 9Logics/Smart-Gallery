import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Remove the Parallax Gallery logic
js = re.sub(
    r'// Skiper 30 Parallax Gallery - Massive Scatter.*?(?=\n\s*// Set backdrop \(Parallax\))',
    '// Skiper 30 Parallax Gallery removed per user preference.',
    js,
    flags=re.DOTALL
)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Removed parallax scatter gallery")
