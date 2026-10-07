import re

with open('app/static/js/globals.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = "&& !request.url.includes('/api/photo/file') && !request.url.includes('/api/photo/thumbnail')) {"

replacement = "&& !request.url.includes('/api/photo/file') && !request.url.includes('/api/photo/thumbnail') && !request.url.includes('/api/data/export') && !request.url.includes('/api/photo/crop')) {"

if target in js:
    # There are two places this occurs in globals.js, one for pywebview bridge and one for caching.
    js = js.replace(target, replacement)
    with open('app/static/js/globals.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched globals.js successfully")
else:
    print("Target not found in globals.js")
