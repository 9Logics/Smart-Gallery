import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """        const wrapper = document.getElementById('custom-video-wrapper');
        const wasVideo = wrapper && !wrapper.classList.contains('hidden');
        if (wrapper) {
            wrapper.classList.add('hidden');"""

replacement = """        const wrapper = document.getElementById('custom-video-wrapper');
        const wasVideo = wrapper && !wrapper.classList.contains('hidden');
        if (wrapper) {
            wrapper.classList.add('hidden');
            const controlsContainer = document.getElementById('custom-video-controls-container');
            if (controlsContainer) controlsContainer.classList.add('hidden');"""

if target in js:
    js = js.replace(target, replacement)
    print("Replaced successfully")
else:
    print("Target not found!")

with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
    f.write(js)
