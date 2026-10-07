import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    if (muteBtn) muteBtn.classList.toggle('hidden', !isVideo);"""

replacement = """    if (muteBtn) {
        muteBtn.classList.toggle('hidden', !isVideo);
        muteBtn.innerHTML = window.storyState.muted ? '<i data-lucide="volume-x"></i>' : '<i data-lucide="volume-2"></i>';
        if (window.lucide) window.lucide.createIcons({ nodes: [muteBtn] });
    }"""

js = js.replace(target, replacement)

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated mute sync!")
