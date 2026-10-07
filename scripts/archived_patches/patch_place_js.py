import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the iconic place assignment
old_place_block = '''            if (data.iconic_place) {
                document.getElementById('recap-stat-place').innerText = data.iconic_place;
            } else {
                document.getElementById('slide-place').style.display = 'none'; // skip
            }
            
            
            // Skiper 30 Parallax Gallery'''

new_place_block = '''            if (data.iconic_place) {
                document.getElementById('recap-stat-place').innerText = data.iconic_place;
                
                const fan = document.getElementById('place-photos-fan');
                fan.innerHTML = '';
                if (data.iconic_place_photos && data.iconic_place_photos.length > 0) {
                    const photos = data.iconic_place_photos;
                    // Distribute fan angles based on number of photos
                    const angles = photos.length === 3 ? [-12, 0, 12] : photos.length === 2 ? [-8, 8] : [0];
                    const zIndices = [1, 3, 2]; // Keep center on top usually
                    
                    photos.forEach((p, idx) => {
                        const div = document.createElement('div');
                        div.className = 'place-fan-photo';
                        div.style.zIndex = zIndices[idx] || 1;
                        div.style.transform = `rotate(${angles[idx] || 0}deg) translateY(${Math.abs(angles[idx] || 0) * 1.5}px)`;
                        div.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(p)}" />`;
                        fan.appendChild(div);
                    });
                }
            } else {
                document.getElementById('slide-place').style.display = 'none'; // skip
            }
            
            // Skiper 30 Parallax Gallery'''

js = js.replace(old_place_block, new_place_block)

# Remove the broken recap-stat-place-img line
js = re.sub(r"document\.getElementById\('recap-stat-place-img'\)\.src = .*?;\n", "", js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated JS for place photos fan!")
