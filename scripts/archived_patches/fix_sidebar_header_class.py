import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('class="sidebar-header"', 'class="lightbox-sidebar-header"')

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(html)
