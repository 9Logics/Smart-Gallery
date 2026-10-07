import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_place_slide = '''            <div class="recap-slide siena-depth" id="slide-place">
                <h2 class="siena-layer" data-depth="20">You explored</h2>
                <div class="iconic-place-card siena-layer" data-depth="60">
                    <img id="recap-stat-place-img" src="" />
                    <div class="sticker-animated">??</div>
                    <h1 class="siena-layer" data-depth="40" id="recap-stat-place"></h1>
                </div>
            </div>'''

# The previous replace might have left the pin as `??` if the terminal messed with encoding, let's use regex or just standard replace
import re
html = re.sub(
    r'<div class="recap-slide siena-depth" id="slide-place">.*?</div>\s*</div>',
    '''<div class="recap-slide siena-depth" id="slide-place">
                <h2 class="siena-layer" data-depth="20">You explored</h2>
                <div id="place-photos-fan" class="siena-layer" data-depth="50"></div>
                <h1 class="siena-layer" data-depth="70" id="recap-stat-place"></h1>
            </div>''',
    html,
    flags=re.DOTALL
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated slide-place HTML structure!")
