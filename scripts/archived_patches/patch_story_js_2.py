import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    card.photos.forEach((p, idx) => {
        const item = document.createElement('div');
        item.className = 'story-grid-item';"""

replacement = """    card.photos.forEach((p, idx) => {
        const item = document.createElement('img');
        item.className = 'story-grid-item';"""

if target in js:
    js = js.replace(target, replacement)
    print("Replaced element creation")
else:
    print("Target 1 not found!")

target2 = """        item.onclick = () => {
            closeStoryViewer();
            if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(idx);
            }
        };"""

replacement2 = """        item.onclick = () => {
            if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(path);
            }
        };"""

if target2 in js:
    js = js.replace(target2, replacement2)
    print("Replaced onclick handler")
else:
    print("Target 2 not found!")

target3 = """        item.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent((path || '').replace(/\\\\\\\\/g, '/'))}")`;"""
# Note: In python we need to be careful with string literals, let's just use regex.

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
