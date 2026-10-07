import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """        item.className = 'story-grid-item';"""
replacement = """        item.className = 'story-grid-item';
        item.dataset.path = path;"""

if target in js:
    js = js.replace(target, replacement)
    print("Added data-path to story grid items")
else:
    print("Target not found in story_viewer.js")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
