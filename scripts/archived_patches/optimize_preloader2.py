import re
js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace moment_photos preload map
js = re.sub(r'if \(data\.moment_photos\) \{\s*preloadUrls = preloadUrls\.concat\(data\.moment_photos\.map[^\}]+\}\s*else', 'if (data.moment_photos) { /* Skip moment_photos full res */ } else', js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print('Fixed preloader')
