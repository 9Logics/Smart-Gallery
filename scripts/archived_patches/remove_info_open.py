import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    d = f.read()

d = d.replace('<div id="lightbox-modal" class="lightbox-modal hidden info-open">', '<div id="lightbox-modal" class="lightbox-modal hidden">')

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(d)
