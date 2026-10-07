import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix vidEl.src
js = re.sub(
    r'vidEl\.src\s*=\s*`/api/photo/file/\$\{encodeURIComponent\(path\)[^`]*\}`;',
    r'vidEl.src = `/api/photo/file/${encodeURIComponent(path)}`;',
    js
)

# Fix imgEl.src
js = re.sub(
    r'imgEl\.src\s*=\s*`/api/photo/file/\$\{encodeURIComponent\(path\)[^`]*\}`;',
    r'imgEl.src = `/api/photo/file/${encodeURIComponent(path)}`;',
    js
)

# Fix item.src (thumbnail)
js = re.sub(
    r'item\.src\s*=\s*`/api/photo/thumbnail/\$\{encodeURIComponent\(\(path[^`]*\}`;',
    r'item.src = `/api/photo/thumbnail/${encodeURIComponent(path)}`;',
    js
)

# Fix prevCardEl thumbnail
js = re.sub(
    r'prevCardEl\.style\.backgroundImage\s*=\s*`url\("/api/photo/thumbnail/\$\{encodeURIComponent\(\(p[^`]*\)"\)`;',
    r'prevCardEl.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent(p)}")`;',
    js
)

# Fix nextCardEl thumbnail
js = re.sub(
    r'nextCardEl\.style\.backgroundImage\s*=\s*`url\("/api/photo/thumbnail/\$\{encodeURIComponent\(\(p[^`]*\)"\)`;',
    r'nextCardEl.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent(p)}")`;',
    js
)

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("URLs fixed!")
