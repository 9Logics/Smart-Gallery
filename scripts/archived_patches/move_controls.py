import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    d = f.read()

# Find the video controls block
controls_pattern = r'(<div id="custom-video-controls-container" class="hidden" style=")([^"]+)(">\s*<div class="custom-video-controls" style=")([^"]+)(")'
match = re.search(controls_pattern, d)
if match:
    # Update styles to make it a floating pill
    new_container_style = 'position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%); width: max-content; display: flex; justify-content: center; background: rgba(15, 22, 38, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); border-radius: 100px; padding: 8px 16px; z-index: 20; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'
    new_inner_style = 'display: flex; align-items: center; gap: 16px; width: max-content; min-width: 350px;'
    
    d = d[:match.start(2)] + new_container_style + d[match.end(2):match.start(4)] + new_inner_style + d[match.end(4):]
    
    # We must move the entire #custom-video-controls-container INSIDE #custom-video-wrapper!
    # Currently it's after #lightbox-media-container or inside it.
    
with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(d)
