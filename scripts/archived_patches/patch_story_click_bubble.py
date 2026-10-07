import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    const wrapper = document.getElementById('story-active-card-wrapper');
    if (wrapper) {
        wrapper.addEventListener('click', (e) => {
            if (e.target.closest('button')) return;
            toggleStoryPause();
        });
    }"""

replacement = """    const wrapper = document.getElementById('story-active-card-wrapper');
    if (wrapper) {
        wrapper.addEventListener('click', (e) => {
            if (e.target.closest('button') || e.target.closest('.story-playback-bar')) return;
            toggleStoryPause();
        });
    }"""

if target in js:
    js = js.replace(target, replacement)
    print("JS wrapper click listener patched!")
else:
    print("Target not found for wrapper click listener!")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
