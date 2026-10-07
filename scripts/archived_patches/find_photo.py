import re
with open('app/static/js/views/photos.js', 'r', encoding='utf-8') as f:
    js = f.read()

m = re.search(r'photosGrid\.innerHTML\s*\+?=\s*`([^`]+)`', js)
if m:
    print(m.group(1)[:500])
else:
    print("Not found inside innerHTML assignment. Looking for photo class:")
    m = re.findall(r'class="([^"]*photo[^"]*)"', js)
    print(set(m))
