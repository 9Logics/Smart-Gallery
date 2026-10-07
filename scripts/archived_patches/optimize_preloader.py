import re
js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Change preloader to NOT fetch moment_photos as full res
old_pre = "if (data.moment_photos) {\n                    preloadUrls = preloadUrls.concat(data.moment_photos.map(p => /api/photo/file/));"
new_pre = "if (data.moment_photos) {\n                    // Marquee uses thumbnails now, so skip full-res preload\n"
js = js.replace(old_pre, new_pre)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
