import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the filmstrip container styles
old_filmstrip_style = '<div id="lightbox-filmstrip-container" class="hidden" style="width: 100%; height: 100px; background: rgba(0, 0, 0, 0.6); padding: 10px; display: flex; align-items: center; gap: 8px; overflow-x: auto; flex-shrink: 0; box-sizing: border-box; scroll-behavior: smooth; border-top: 1px solid rgba(255,255,255,0.05);">'
new_filmstrip_style = '<div id="lightbox-filmstrip-container" class="hidden" style="width: 100%; height: 85px; background: rgba(9, 13, 22, 0.85); backdrop-filter: blur(20px); padding: 10px 24px; display: flex; align-items: center; gap: 12px; overflow-x: auto; flex-shrink: 0; box-sizing: border-box; scroll-behavior: smooth; border-top: 1px solid rgba(255,255,255,0.08); z-index: 50;">'

html = html.replace(old_filmstrip_style, new_filmstrip_style)

# 2. Extract controls and place inside custom-video-wrapper
# Find custom-video-wrapper
start_wrapper = html.find('<div id="custom-video-wrapper"')
end_wrapper = html.find('</div>\n                        \n                        <!-- Video Loading & Error States -->', start_wrapper)
# Actually, let's just find the closing tag of video
video_tag_end = html.find('</video>', start_wrapper) + 8

# Find custom-video-controls-container
start_controls = html.find('<div id="custom-video-controls-container"')
# Find matching end div for controls container
# Count divs
count = 0
i = start_controls
while i < len(html):
    if html[i:i+4] == '<div':
        count += 1
    elif html[i:i+5] == '</div':
        count -= 1
        if count == 0:
            end_controls = i + 6
            break
    i += 1

controls_html = html[start_controls:end_controls]

# Update the inline styles of controls container and its inner div
controls_html = re.sub(
    r'(<div id="custom-video-controls-container"[^>]*?style=")([^"]+)(")',
    r'\1position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); width: max-content; display: flex; justify-content: center; background: rgba(15, 22, 38, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); border-radius: 100px; padding: 10px 20px; z-index: 40; box-shadow: 0 10px 30px rgba(0,0,0,0.5);\3',
    controls_html
)

controls_html = re.sub(
    r'(<div class="custom-video-controls"[^>]*?style=")([^"]+)(")',
    r'\1width: max-content; min-width: 400px; display: flex; align-items: center; gap: 16px;\3',
    controls_html
)

# Remove old controls from html
html = html[:start_controls] + html[end_controls:]

# Insert controls after video tag
video_tag_end = html.find('</video>') + 8
html = html[:video_tag_end] + '\n' + controls_html + html[video_tag_end:]

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(html)
