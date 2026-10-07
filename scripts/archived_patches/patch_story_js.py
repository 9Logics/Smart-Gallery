import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    card.photos.forEach((p, idx) => {
        const item = document.createElement('div');
        item.className = 'story-grid-item';
        let path = p.path || p.file_path || '';
        item.style.backgroundImage = `url("/api/photo/thumbnail/${encodeURIComponent((path || '').replace(/\\\\/g, '/'))}")`;
        item.onclick = () => {
            closeStoryViewer();
            if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(idx);
            }
        };
        content.appendChild(item);
    });"""

replacement = """    card.photos.forEach((p, idx) => {
        const item = document.createElement('img');
        item.className = 'story-grid-item';
        let path = p.path || p.file_path || '';
        item.src = `/api/photo/thumbnail/${encodeURIComponent((path || '').replace(/\\\\/g, '/'))}`;
        item.onclick = () => {
            // Do NOT close the story viewer, just open lightbox on top
            if (window.state && window.openLightbox) {
                window.state.lightboxPhotos = card.photos;
                window.openLightbox(path);
            }
        };
        content.appendChild(item);
    });"""

if target in js:
    js = js.replace(target, replacement)
    print("JS updated successfully!")
else:
    print("JS target not found!")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
