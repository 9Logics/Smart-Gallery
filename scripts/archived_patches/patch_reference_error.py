import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """        item.className = 'story-grid-item';
        item.dataset.path = path;
        let path = p.path || p.file_path || '';"""

replacement = """        item.className = 'story-grid-item';
        let path = p.path || p.file_path || '';
        item.dataset.path = path;"""

if target in js:
    js = js.replace(target, replacement)
    print("Fixed ReferenceError in story_viewer.js")
else:
    print("Target not found in story_viewer.js")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
