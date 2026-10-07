import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Strip inline styles from lightbox-filmstrip-container
old_tag = '<div id="lightbox-filmstrip-container" class="hidden" style="width: 100%; height: 85px; background: rgba(9, 13, 22, 0.85); backdrop-filter: blur(20px); padding: 10px 24px; display: flex; align-items: center; gap: 12px; overflow-x: auto; flex-shrink: 0; box-sizing: border-box; scroll-behavior: smooth; border-top: 1px solid rgba(255,255,255,0.08); z-index: 50;">'
new_tag = '<div id="lightbox-filmstrip-container" class="hidden">'

if old_tag in html:
    html = html.replace(old_tag, new_tag)
else:
    # Use regex in case spacing differs
    html = re.sub(
        r'<div id="lightbox-filmstrip-container" class="hidden" style="[^"]+">',
        new_tag,
        html
    )

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(html)
