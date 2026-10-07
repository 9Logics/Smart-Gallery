import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

layer = '''
        <!-- Dynamic Slide Transition Layer -->
        <div id="recap-slide-transition" style="position: absolute; inset: 0; pointer-events: none; z-index: 10001; display: none;"></div>
        
        <div id="recap-slides-container" class="hidden">'''

if 'id="recap-slide-transition"' not in html:
    html = html.replace('<div id="recap-slides-container" class="hidden">', layer)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added transition layer!")
