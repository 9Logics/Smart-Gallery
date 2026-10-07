import re
js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Marquee photos
js = js.replace('src="/api/photo/file/" loading="lazy"', 'src="/api/photo/thumbnail/" loading="lazy"')

# Montage burst photos
js = js.replace('<img src="/api/photo/file/" />', '<img src="/api/photo/thumbnail/" />')

# Transition transitions (skiper-32, 33, 30, 71, 79)
js = js.replace("img.src = '/api/photo/file/' + encodeURIComponent(p);", "img.src = '/api/photo/thumbnail/' + encodeURIComponent(p);")
js = js.replace("img.src = '/api/photo/file/' + encodeURIComponent(photos[i % photos.length]);", "img.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[i % photos.length]);")
js = js.replace("img.src = '/api/photo/file/' + encodeURIComponent(pool[i]);", "img.src = '/api/photo/thumbnail/' + encodeURIComponent(pool[i]);")
js = js.replace("bgImg.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);", "bgImg.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);")
js = js.replace("midImg.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);", "midImg.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);")
js = js.replace("fgImg.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);", "fgImg.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);")
js = js.replace("img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);", "img.src = '/api/photo/thumbnail/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print('Optimized JS for thumbnail usage!')
