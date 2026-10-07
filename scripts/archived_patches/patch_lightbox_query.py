import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = 'const thumbImg = document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img`);'
replacement = 'const thumbImg = document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img, .story-grid-item[data-path="${CSS.escape(path)}"]`);'

if target in js:
    js = js.replace(target, replacement)
    print("lightbox.js querySelector updated!")
else:
    print("Target not found in lightbox.js")

target2 = 'const thumbImg = path ? document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img`) : null;'
replacement2 = 'const thumbImg = path ? document.querySelector(`.photo-card[data-path="${CSS.escape(path)}"] img, .story-grid-item[data-path="${CSS.escape(path)}"]`) : null;'

if target2 in js:
    js = js.replace(target2, replacement2)
    print("lightbox.js close querySelector updated!")
else:
    print("Target2 not found in lightbox.js")

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
