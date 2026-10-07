import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target1 = "vidEl.src = `/api/photo/file/${encodeURIComponent(path).replace(/%5C/g, '\\\\').replace(/%2F/g, '/')}`;"
replacement1 = "vidEl.src = `/api/photo/file/${encodeURIComponent(path)}`;"

target2 = "imgEl.src = `/api/photo/file/${encodeURIComponent(path).replace(/%5C/g, '\\\\').replace(/%2F/g, '/')}`;"
replacement2 = "imgEl.src = `/api/photo/file/${encodeURIComponent(path)}`;"

target3 = "item.src = `/api/photo/thumbnail/${encodeURIComponent((path || '').replace(/\\\\\\\\/g, '/'))}`;"
# Note: the thumbnail url had .replace(/\\\\/g, '/') BEFORE encodeURIComponent. Wait...
# Let's just fix it generically.
