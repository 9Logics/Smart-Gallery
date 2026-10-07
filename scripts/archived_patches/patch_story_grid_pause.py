import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """    clearStoryTimer();
    gridView.classList.remove('hidden');"""

replacement = """    clearStoryTimer();
    
    // Ensure story is paused
    const vidEl = document.getElementById('story-video');
    if (vidEl && !vidEl.paused) vidEl.pause();
    window.storyState.isPaused = true;
    
    const indicator = document.getElementById('story-play-indicator');
    if (indicator) {
        indicator.innerHTML = `<i data-lucide="play"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [indicator] });
    }
    const playBtn = document.getElementById('story-play-pause-btn');
    if (playBtn) {
        playBtn.innerHTML = `<i data-lucide="play"></i>`;
        if (window.lucide) window.lucide.createIcons({ nodes: [playBtn] });
    }
    
    gridView.classList.remove('hidden');"""

if target in js:
    js = js.replace(target, replacement)
    print("JS patched for pausing!")
else:
    print("JS target not found!")

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
