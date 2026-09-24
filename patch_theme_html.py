import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

goo_svg = '''
        <!-- SVG Filter for Gooey Theme -->
        <svg style="position: absolute; width: 0; height: 0; pointer-events: none;">
            <defs>
                <filter id="recap-goo">
                    <feGaussianBlur in="SourceGraphic" stdDeviation="40" result="blur"></feGaussianBlur>
                    <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 50 -20" result="goo"></feColorMatrix>
                    <feComposite in="SourceGraphic" in2="goo" operator="atop"></feComposite>
                </filter>
            </defs>
        </svg>
        <div class="recap-backdrop" id="recap-backdrop"></div>
        <div id="theme-canvas"></div>
'''

if '<div id="theme-canvas"></div>' not in html:
    html = html.replace('<div class="recap-backdrop" id="recap-backdrop"></div>', goo_svg)
    html = html.replace('v=275', 'v=276')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Injected Theme Canvas HTML!")
else:
    print("Theme Canvas already injected.")
