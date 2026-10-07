import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Find the start of the custom-video-controls-container
controls_start = html.find('<div id="custom-video-controls-container"')
# 2. Find the end of it (count divs)
count = 0
i = controls_start
while i < len(html):
    if html[i:i+4] == '<div':
        count += 1
    elif html[i:i+5] == '</div':
        count -= 1
        if count == 0:
            controls_end = i + 6
            break
    i += 1

controls_html = html[controls_start:controls_end]

# 3. Remove from current position
html = html[:controls_start] + html[controls_end:]

# 4. Find the end of lightbox-morph-frame
# Which is after: <div id="lightbox-drawing-overlay" ...></div>\n</div>
drawing_overlay_end = html.find('<div id="lightbox-drawing-overlay"')
# Find its closing tag
drawing_end = html.find('</div>', drawing_overlay_end) + 6
# Next closing tag is the end of lightbox-morph-frame
morph_end = html.find('</div>', drawing_end) + 6

# 5. Modify the controls HTML to NOT be position absolute, but rather a flow element or at least positioned relative to the parent
# Actually, since it will be a sibling in `#lightbox-media-container` (which is a flex column), we can just remove `position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);` and replace it with `margin-top: 16px;`
# But wait, it's a flex column with `justify-content: center`.
# If I make it a sibling, it will sit below the video frame, naturally!
controls_html = controls_html.replace('position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);', 'margin-top: 16px;')

# 6. Insert after morph_end
html = html[:morph_end] + '\n' + controls_html + html[morph_end:]

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(html)
