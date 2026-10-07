import re

with open('app/static/js/story_viewer.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """                vidEl.ontimeupdate = () => {
                    if (vidEl.duration) fill.style.width = (vidEl.currentTime / vidEl.duration * 100) + '%';
                };"""

replacement = """                vidEl.ontimeupdate = () => {
                    if (vidEl.duration) {
                        const pct = (vidEl.currentTime / vidEl.duration * 100);
                        fill.style.width = pct + '%';
                        const seekEl = document.getElementById('story-video-seek');
                        if (seekEl && !seekEl.isDragging) seekEl.value = pct;
                    }
                };"""

if target in js:
    js = js.replace(target, replacement)
    print("JS ontimeupdate patched!")
else:
    print("Target not found for ontimeupdate!")

target2 = """    if (isVideo) {
        vidEl.src = `/api/photo/file/${encodeURIComponent(path).replace(/%5C/g, '\\\\').replace(/%2F/g, '/')}`;"""

replacement2 = """    const seekContainer = document.getElementById('story-video-seek-container');
    const spacer = document.getElementById('story-spacer');
    if (seekContainer) seekContainer.classList.toggle('hidden', !isVideo);
    if (spacer) spacer.classList.toggle('hidden', isVideo);
    
    if (isVideo) {
        vidEl.src = `/api/photo/file/${encodeURIComponent(path).replace(/%5C/g, '\\\\').replace(/%2F/g, '/')}`;"""

if target2 in js:
    js = js.replace(target2, replacement2)
    print("JS hide/show seek bar patched!")
else:
    print("Target not found for hide/show seek bar!")

# Add event listeners for seeking in initStoryViewer
target3 = """    document.getElementById('story-play-pause-btn')?.addEventListener('click', (e) => { e.stopPropagation(); toggleStoryPause(); });"""

replacement3 = """    document.getElementById('story-play-pause-btn')?.addEventListener('click', (e) => { e.stopPropagation(); toggleStoryPause(); });
    
    const seekEl = document.getElementById('story-video-seek');
    if (seekEl) {
        seekEl.addEventListener('mousedown', () => seekEl.isDragging = true);
        seekEl.addEventListener('mouseup', () => seekEl.isDragging = false);
        seekEl.addEventListener('input', (e) => {
            const vidEl = document.getElementById('story-video');
            if (vidEl && vidEl.duration) {
                vidEl.currentTime = (e.target.value / 100) * vidEl.duration;
            }
        });
    }"""

if target3 in js:
    js = js.replace(target3, replacement3)
    print("JS seek event listener patched!")
else:
    print("Target not found for seek event listener!")


with open('app/static/js/story_viewer.js', 'w', encoding='utf-8') as f:
    f.write(js)
