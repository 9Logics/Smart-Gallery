import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Make sure we unhide story-mute-btn for videos
target1 = """    const seekContainer = document.getElementById('story-video-seek-container');
    const spacer = document.getElementById('story-spacer');
    if (seekContainer) seekContainer.classList.toggle('hidden', !isVideo);
    if (spacer) spacer.classList.toggle('hidden', isVideo);"""

replacement1 = """    const seekContainer = document.getElementById('story-video-seek-container');
    const spacer = document.getElementById('story-spacer');
    const muteBtn = document.getElementById('story-mute-btn');
    if (seekContainer) seekContainer.classList.toggle('hidden', !isVideo);
    if (spacer) spacer.classList.toggle('hidden', isVideo);
    if (muteBtn) muteBtn.classList.toggle('hidden', !isVideo);"""

js = js.replace(target1, replacement1)

# Ensure the 'M' key works
target2 = """    window.addEventListener('keydown', (e) => {
        if (!window.storyState || !window.storyState.isActive) return;
        if (e.key === 'Escape') closeStoryViewer();
        if (e.key === 'ArrowRight') nextStoryMedia();
        if (e.key === 'ArrowLeft') prevStoryMedia();
        if (e.key === ' ') { e.preventDefault(); toggleStoryPause(); }
    });"""

replacement2 = """    window.addEventListener('keydown', (e) => {
        if (!window.storyState || !window.storyState.isActive) return;
        if (e.key === 'Escape') closeStoryViewer();
        if (e.key === 'ArrowRight') nextStoryMedia();
        if (e.key === 'ArrowLeft') prevStoryMedia();
        if (e.key === ' ') { e.preventDefault(); toggleStoryPause(); }
        if (e.key.toLowerCase() === 'm') { e.preventDefault(); toggleStoryMute(); }
    });"""

js = js.replace(target2, replacement2)

with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated story_viewer.js with mute toggles and 'm' keybind!")
