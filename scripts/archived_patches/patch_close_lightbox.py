import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    if (spinner) spinner.classList.add('hidden');
    if (errMsg) errMsg.classList.add('hidden');
    elements.lightboxVideo.pause();"""

replacement = """    if (spinner) spinner.classList.add('hidden');
    if (errMsg) errMsg.classList.add('hidden');
    elements.lightboxVideo.pause();
    const controlsContainer = document.getElementById('custom-video-controls-container');
    if (controlsContainer) controlsContainer.classList.add('hidden');"""

if target in js:
    js = js.replace(target, replacement)
    print("Replaced closeLightbox")
else:
    print("Target not found in lightbox.js")

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(js)
