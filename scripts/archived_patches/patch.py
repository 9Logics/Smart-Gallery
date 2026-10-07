import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    d = f.read()

# 1. Update the main controls bar style
old_style = 'style="position: absolute; bottom: 15px; left: 15px; right: 15px; z-index: 10; display: flex; align-items: center; gap: 12px; background: rgba(15, 22, 38, 0.85); backdrop-filter: blur(8px); padding: 8px 16px; border-radius: 12px; border: 1px solid var(--border-color); opacity: 0; transition: opacity 0.25s;"'
new_style = 'style="position: fixed; bottom: 40px; left: 50%; transform: translateX(-50%); width: 700px; max-width: 90vw; z-index: 9999; display: flex; align-items: center; gap: 16px; background: rgba(15, 22, 38, 0.95); backdrop-filter: blur(16px); padding: 12px 24px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); opacity: 0; transition: opacity 0.25s, transform 0.25s; box-shadow: 0 10px 40px rgba(0,0,0,0.5);"'
d = d.replace(old_style, new_style)

# 2. Update the video timeline styling
old_timeline = '<input type="range" id="video-timeline" min="0" max="100" value="0" style="flex-grow:1; cursor:pointer;" />'
new_timeline = '<input type="range" id="video-timeline" min="0" max="100" value="0" style="flex-grow:1; cursor:pointer; height: 6px; border-radius: 4px; outline: none; -webkit-appearance: none; background: rgba(255,255,255,0.2);" />'
d = d.replace(old_timeline, new_timeline)

# 3. Group mute button and volume slider to make hover scrolling easy
old_volume_section = '''<button id="video-mute-btn" class="btn-icon" style="background:transparent; padding:0; width:32px; height:32px;" title="Mute/Unmute"><i data-lucide="volume-2" style="width:18px; height:18px;"></i></button>
                            <input type="range" id="video-volume" min="0" max="1" step="0.05" value="1" style="width: 60px; cursor: pointer; accent-color: #3b82f6;" title="Volume" />'''

new_volume_section = '''<div id="video-volume-container" style="display: flex; align-items: center; gap: 8px; padding: 4px; border-radius: 8px;">
                                <button id="video-mute-btn" class="btn-icon" style="background:transparent; padding:0; width:32px; height:32px;" title="Mute/Unmute"><i data-lucide="volume-2" style="width:18px; height:18px;"></i></button>
                                <input type="range" id="video-volume" min="0" max="1" step="0.05" value="1" style="width: 80px; cursor: pointer; accent-color: var(--accent-color); height: 6px; border-radius: 4px; outline: none; -webkit-appearance: none; background: rgba(255,255,255,0.2);" title="Volume" />
                            </div>'''
d = d.replace(old_volume_section, new_volume_section)

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(d)
