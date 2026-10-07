import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the outer container to be wider
old_outer = 'style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); width: max-content; display: flex; justify-content: center; background: rgba(15, 22, 38, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); border-radius: 100px; padding: 10px 20px; z-index: 40; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"'
new_outer = 'style="position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); width: 85%; max-width: 900px; display: flex; justify-content: center; background: rgba(15, 22, 38, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); border-radius: 100px; padding: 10px 24px; z-index: 40; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"'
html = html.replace(old_outer, new_outer)

# 2. Update the inner container to take full width
old_inner = 'style="width: max-content; min-width: 400px; display: flex; align-items: center; gap: 16px;"'
new_inner = 'style="width: 100%; display: flex; align-items: center; gap: 16px;"'
html = html.replace(old_inner, new_inner)

# 3. Update the volume container to remove the gap and let CSS handle spacing
old_vol_container = 'style="display: flex; align-items: center; gap: 8px; padding: 4px; border-radius: 8px;"'
new_vol_container = 'class="video-volume-container" style="display: flex; align-items: center; padding: 4px; border-radius: 100px; transition: background 0.3s;"'
html = html.replace(old_vol_container, new_vol_container)

# 4. Remove inline styles from the volume slider (we'll move them to style.css)
old_slider = 'style="width: 80px; cursor: pointer; accent-color: var(--accent-color); height: 6px; border-radius: 4px; outline: none; -webkit-appearance: none; background: rgba(255,255,255,0.2);"'
new_slider = 'class="video-volume-slider"'
html = html.replace(old_slider, new_slider)

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(html)
