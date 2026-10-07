import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target_pause = """    if (indicator) {
        indicator.innerHTML = `<i data-lucide="${icon}"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [indicator] });
        indicator.classList.add('active');
        setTimeout(() => indicator.classList.remove('active'), 600);
    }"""

replacement_pause = """    if (indicator) {
        indicator.innerHTML = `<i data-lucide="${icon}"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [indicator] });
        indicator.classList.add('active');
        setTimeout(() => indicator.classList.remove('active'), 600);
    }
    
    const playBtn = document.getElementById('story-play-pause-btn');
    if (playBtn) {
        playBtn.innerHTML = `<i data-lucide="${icon}"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [playBtn] });
    }"""

if target_pause in js:
    js = js.replace(target_pause, replacement_pause)
    print("JS updated pause logic!")
else:
    print("Failed to update JS pause logic")

target_init = """    document.getElementById('story-close-btn')?.addEventListener('click', closeStoryViewer);
    document.getElementById('story-mute-btn')?.addEventListener('click', toggleStoryMute);"""

replacement_init = """    document.getElementById('story-close-btn')?.addEventListener('click', closeStoryViewer);
    document.getElementById('story-mute-btn')?.addEventListener('click', toggleStoryMute);
    document.getElementById('story-play-pause-btn')?.addEventListener('click', (e) => { e.stopPropagation(); toggleStoryPause(); });"""

if target_init in js:
    js = js.replace(target_init, replacement_init)
    print("JS updated init listeners!")
else:
    print("Failed to update JS init listeners")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
