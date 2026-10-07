js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace('argBytesPerMonth', 'avgBytesPerMonth')

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
