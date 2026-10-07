import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

montage_slide = '''            <div class="recap-slide siena-depth" id="slide-montage">
                <div id="montage-container" class="siena-layer" data-depth="50"></div>
            </div>
            
            <div class="recap-slide siena-depth" id="slide-intro">'''

html = html.replace('<div class="recap-slide active siena-depth" id="slide-intro">', montage_slide)
# Also fix double class on slide-person and slide-place
html = html.replace('id="recap-stat-person" class="highlight-text"', 'id="recap-stat-person"')
html = html.replace('id="recap-stat-place" class="highlight-text"', 'id="recap-stat-place"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Added montage slide to HTML!")
