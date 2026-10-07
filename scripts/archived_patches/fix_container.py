js_path = 'app/static/js/views/stats.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

bad_str = "if (container) {"
good_str = "const container = document.getElementById('forecast-svg-container');\n                if (container) {"

if bad_str in js:
    js = js.replace(bad_str, good_str)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("FIXED CONTAINER")
else:
    print("NOT FOUND")
