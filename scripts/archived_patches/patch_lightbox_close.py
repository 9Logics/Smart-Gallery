import re

with open('app/static/js/lightbox.js', 'r', encoding='utf-8') as f:
    d = f.read()

# Replace completeClose
old_close = '''function completeClose() {
    elements.lightbox.classList.add('hidden');
    elements.lightbox.style.animation = '';
    state.lightboxIndex = -1;
    resetZoom();'''

new_close = '''function completeClose() {
    elements.lightbox.classList.add('hidden');
    elements.lightbox.classList.remove('info-open');
    elements.lightbox.style.animation = '';
    state.lightboxIndex = -1;
    resetZoom();'''

d = d.replace(old_close, new_close)

with open('app/static/js/lightbox.js', 'w', encoding='utf-8') as f:
    f.write(d)
