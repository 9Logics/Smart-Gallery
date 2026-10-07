import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target_idle = """.story-card-overlays.idle .story-card-top-left {"""
replacement_idle = """.story-card-overlays.idle .story-playback-bar,
.story-card-overlays.idle .story-card-top-left {"""

if target_idle in css:
    css = css.replace(target_idle, replacement_idle)
    print("CSS updated idle!")
else:
    print("Failed to update CSS idle")
    
target_trans = """.story-nav-arrow, .story-grid-bottom-btn, .story-card-top-left {"""
replacement_trans = """.story-nav-arrow, .story-grid-bottom-btn, .story-card-top-left, .story-playback-bar {"""

if target_trans in css:
    css = css.replace(target_trans, replacement_trans)
    print("CSS updated transitions!")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
