import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    d = f.read()

# Replace timeline input logic with mousedown pause logic
old_timeline_logic = '''            timeline.addEventListener('input', () => {
                if (video.duration) {
                    video.currentTime = (timeline.value / 100) * video.duration;
                    const pct = timeline.value;
                    timeline.style.background = `linear-gradient(to right, var(--accent-color) ${pct}%, rgba(255, 255, 255, 0.3) ${pct}%)`;
                }
            });'''
# Let's write a regex search because the color might be #3b82f6 or var(--accent-color)
import re

replacement_timeline = '''            timeline.addEventListener('input', () => {
                if (video.duration) {
                    video.currentTime = (timeline.value / 100) * video.duration;
                    const pct = timeline.value;
                    timeline.style.background = `linear-gradient(to right, var(--accent-color) ${pct}%, rgba(255, 255, 255, 0.3) ${pct}%)`;
                }
            });
            
            timeline.addEventListener('mousedown', () => {
                video.pause();
            });'''

d = re.sub(r'timeline\.addEventListener\(\'input\'[\s\S]*?\}\);', replacement_timeline, d, count=1)
d = d.replace('#3b82f6', 'var(--accent-color)') # fix hardcoded blue in timeline gradients

# Setup Volume Scroll & Memory & M shortcut
old_volume = '''        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                video.volume = e.target.value;
                video.muted = (video.volume == 0);
                if (video.volume > 0) {
                    state.lastUnmutedVolume = video.volume;
                }
                updateVolumeUI();
            });
        }'''

new_volume = '''        if (volumeSlider) {
            const savedVol = localStorage.getItem('playerVolume');
            if (savedVol !== null) {
                video.volume = parseFloat(savedVol);
                state.lastUnmutedVolume = video.volume > 0 ? video.volume : 1.0;
                video.muted = (video.volume === 0);
            }
            
            volumeSlider.addEventListener('input', (e) => {
                video.volume = e.target.value;
                video.muted = (video.volume == 0);
                if (video.volume > 0) {
                    state.lastUnmutedVolume = video.volume;
                }
                localStorage.setItem('playerVolume', video.volume);
                updateVolumeUI();
            });
            
            const volContainer = document.getElementById('video-volume-container');
            if (volContainer) {
                volContainer.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    let step = 0.05;
                    let newVol = video.volume + (e.deltaY < 0 ? step : -step);
                    newVol = Math.max(0, Math.min(1, newVol));
                    
                    video.volume = newVol;
                    video.muted = (newVol === 0);
                    if (newVol > 0) state.lastUnmutedVolume = newVol;
                    volumeSlider.value = newVol;
                    localStorage.setItem('playerVolume', newVol);
                    updateVolumeUI();
                });
            }
            
            document.addEventListener('keydown', (e) => {
                if (e.key.toLowerCase() === 'm' && !document.querySelector('input:focus')) {
                    if (document.getElementById('lightbox-modal') && !document.getElementById('lightbox-modal').classList.contains('hidden')) {
                        muteBtn.click();
                    }
                }
            });
        }'''
d = d.replace(old_volume, new_volume)

with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
    f.write(d)
