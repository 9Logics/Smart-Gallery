import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove story-mute-btn from screen controls
target_remove_mute = """                <div class="story-controls-right">
                    <button id="story-mute-btn" class="btn-icon"><i data-lucide="volume-x"></i></button>
                </div>"""
html = html.replace(target_remove_mute, """                <div class="story-controls-right">
                    <!-- Moved to bottom playback bar -->
                </div>""")

# 2. Add story-playback-bar and move story-progress-container into it
target_progress = """                    <div id="story-progress-container" class="story-progress-container"></div>"""
replacement_progress = """                    <!-- Bottom Playback Controls -->
                    <div class="story-playback-bar">
                        <button id="story-play-pause-btn" class="btn-icon story-bottom-btn"><i data-lucide="pause"></i></button>
                        <div id="story-progress-container" class="story-progress-container"></div>
                        <button id="story-mute-btn" class="btn-icon story-bottom-btn"><i data-lucide="volume-2"></i></button>
                    </div>"""
html = html.replace(target_progress, replacement_progress)

if replacement_progress in html:
    print("HTML updated!")
else:
    print("Failed to update HTML")

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
