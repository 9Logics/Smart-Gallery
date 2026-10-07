import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = """                  <!-- Inner Overlays -->
                  <div class="story-card-overlays">
                      
                      <!-- Bottom Playback Controls -->
                      <div class="story-playback-bar">
                          <button id="story-play-pause-btn" class="btn-icon story-bottom-btn"><i data-lucide="pause"></i></button>
                          <div id="story-progress-container" class="story-progress-container"></div>
                          <button id="story-mute-btn" class="btn-icon story-bottom-btn"><i data-lucide="volume-2"></i></button>
                      </div>"""

replacement = """                  <!-- Inner Overlays -->
                  <div class="story-card-overlays">
                      
                      <!-- Segmented Progress Bar (at top) -->
                      <div id="story-progress-container" class="story-progress-container"></div>
                      
                      <!-- Bottom Playback Controls -->
                      <div class="story-playback-bar">
                          <button id="story-play-pause-btn" class="btn-icon story-bottom-btn"><i data-lucide="pause"></i></button>
                          <!-- Continuous Seek Bar (videos only) -->
                          <div id="story-video-seek-container" class="story-video-seek-container hidden">
                              <input type="range" id="story-video-seek" min="0" max="100" step="0.1" value="0" class="story-video-range" />
                          </div>
                          <!-- Blank spacer for photos to keep buttons aligned if needed, though hidden works -->
                          <button id="story-mute-btn" class="btn-icon story-bottom-btn hidden"><i data-lucide="volume-2"></i></button>
                      </div>"""

if target in html:
    html = html.replace(target, replacement)
    print("HTML updated!")
else:
    print("Target not found in index.html!")

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
