import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the inner overlays part
pattern = re.compile(r'(<!-- Inner Overlays -->\s*<div class="story-card-overlays">)\s*<!-- Bottom Playback Controls -->\s*<div class="story-playback-bar">.*?</div>', re.DOTALL)

replacement = r'''\1
                    <!-- Segmented Progress Bar (at top) -->
                    <div id="story-progress-container" class="story-progress-container"></div>
                    
                    <!-- Bottom Playback Controls -->
                    <div class="story-playback-bar">
                        <button id="story-play-pause-btn" class="btn-icon story-bottom-btn"><i data-lucide="pause"></i></button>
                        <!-- Continuous Seek Bar (videos only) -->
                        <div id="story-video-seek-container" class="story-video-seek-container hidden" style="flex:1; display: flex; align-items: center;">
                            <input type="range" id="story-video-seek" min="0" max="100" step="0.1" value="0" class="story-video-range" style="width: 100%; cursor: pointer; accent-color: white; height: 4px; border-radius: 2px; outline: none;" />
                        </div>
                        <div id="story-spacer" style="flex:1;"></div>
                        <button id="story-mute-btn" class="btn-icon story-bottom-btn hidden"><i data-lucide="volume-2"></i></button>
                    </div>'''

html, count = pattern.subn(replacement, html)
if count > 0:
    print("HTML updated!")
else:
    print("Failed to replace via regex!")

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
