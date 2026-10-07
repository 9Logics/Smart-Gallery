import re

js_path = 'app/static/js/recap_dashboard.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace thumbnail with file for hero banner
js = js.replace("url('/api/photo/thumbnail/')", "url('/api/photo/file/')")
# Remove opacity 0.5
js = js.replace("heroBg.style.opacity = '0.5';", "heroBg.style.opacity = '1';")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print('Optimized recap_dashboard.js')
