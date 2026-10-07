import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """        item.onclick = () => {
            if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(path);
            }
        };"""

replacement = """        item.onclick = () => {
            if (typeof state !== 'undefined' && typeof openLightbox === 'function') {
                state.lightboxPhotos = card.photos;
                openLightbox(path);
            } else if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(path);
            }
        };"""

if target in js:
    js = js.replace(target, replacement)
    print("JS onclick updated!")
else:
    print("Target not found!")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
