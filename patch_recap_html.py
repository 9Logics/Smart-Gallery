import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

recap_player_html = '''
    <!-- RECAP PLAYER OVERLAY -->
    <div id="recap-player-overlay" class="hidden">
        <div class="recap-backdrop" id="recap-backdrop"></div>
        
        <div id="recap-preloader" class="recap-preloader-screen">
            <div class="preloader-text">Loading Memories...</div>
            <div class="preloader-progress-bar"><div id="recap-progress-fill"></div></div>
        </div>
        
        <div id="recap-slides-container" class="hidden">
            <div class="recap-slide active" id="slide-intro">
                <h1 id="recap-ai-comment"></h1>
            </div>
            <div class="recap-slide" id="slide-stats">
                <h2>You captured</h2>
                <div class="recap-stat-number" id="recap-stat-photos">0</div>
                <p>Photos</p>
                <h2>and</h2>
                <div class="recap-stat-number" id="recap-stat-videos">0</div>
                <p>Videos</p>
            </div>
            <div class="recap-slide" id="slide-person">
                <h2>You spent the most time with</h2>
                <h1 id="recap-stat-person" class="highlight-text"></h1>
            </div>
            <div class="recap-slide" id="slide-place">
                <h2>You explored</h2>
                <div class="iconic-place-card">
                    <img id="recap-stat-place-img" src="" />
                    <div class="sticker-animated">📍</div>
                    <h1 id="recap-stat-place" class="highlight-text"></h1>
                </div>
            </div>
        </div>
        
        <div class="recap-nav-left" onclick="prevRecapSlide()"></div>
        <div class="recap-nav-right" onclick="nextRecapSlide()"></div>
        <div class="recap-close" onclick="closeRecapPlayer()">✕</div>
    </div>
'''

if 'id="recap-player-overlay"' not in html:
    # Insert before the last closing body tag
    html = html.replace('</body>', recap_player_html + '\n</body>')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added recap player HTML!")
else:
    print("Recap player HTML already exists.")

