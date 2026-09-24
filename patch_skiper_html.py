import os
import re

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Skiper15 Preloader Box
old_preloader = '''        <div id="recap-preloader" class="recap-preloader-screen">
            <div class="preloader-text">Loading Memories...</div>
            <div class="preloader-progress-bar"><div id="recap-progress-fill"></div></div>
        </div>'''
new_preloader = '''        <div id="recap-preloader" class="recap-preloader-screen">
            <div class="box-preloader-container">
                <div class="box-3d">
                    <div class="box-face front"></div>
                    <div class="box-face back"></div>
                    <div class="box-face right"></div>
                    <div class="box-face left"></div>
                    <div class="box-face top"></div>
                    <div class="box-face bottom"></div>
                </div>
            </div>
            <div class="preloader-text">Building Journey...</div>
        </div>'''
if 'box-preloader-container' not in html:
    html = html.replace(old_preloader, new_preloader)

# 2. Skiper 30 Parallax Backdrop container (injecting after recap-backdrop)
if '<div class="parallax-gallery-container"' not in html:
    html = html.replace('<div class="recap-backdrop" id="recap-backdrop"></div>', 
                        '<div class="recap-backdrop" id="recap-backdrop"></div>\n        <div class="parallax-gallery-container" id="recap-parallax-gallery"></div>')

# 3. Skiper 19 SVG Path + Skiper 29 Siena Depth
siena_svg = '''
            <div class="skiper19-line-container">
                <svg width="100%" height="100%" viewBox="0 0 1000 1000" preserveAspectRatio="none" fill="none">
                    <path class="skiper19-path" d="M100,500 C300,100 700,900 900,500" stroke="white" stroke-width="4" stroke-opacity="0.2"/>
                </svg>
            </div>
'''
if 'skiper19-line-container' not in html:
    html = html.replace('<div id="recap-slides-container" class="hidden">', '<div id="recap-slides-container" class="hidden">\n' + siena_svg)

# Add siena-depth and siena-layer classes
html = html.replace('class="recap-slide active"', 'class="recap-slide active siena-depth"')
html = html.replace('class="recap-slide"', 'class="recap-slide siena-depth"')
html = html.replace('<h1', '<h1 class="siena-layer" data-depth="40"')
html = html.replace('<h2', '<h2 class="siena-layer" data-depth="20"')
html = html.replace('<div class="iconic-place-card"', '<div class="iconic-place-card siena-layer" data-depth="60"')

# Change stat wrappers to number-flow-wrapper
html = html.replace('class="recap-stat-number"', 'class="number-flow-wrapper"')

html = html.replace('v=277', 'v=278')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Injected Skiper HTML features!")
