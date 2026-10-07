import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_person_block = '''            if (data.top_person) {
                document.getElementById('recap-stat-person').innerText = data.top_person || "Yourself!";
            } else {
                document.getElementById('slide-person').style.display = 'none'; // skip
            }'''

new_person_block = '''            if (data.top_person) {
                document.getElementById('recap-stat-person').innerText = data.top_person || "Yourself!";
                
                const personFan = document.getElementById('person-photos-fan');
                if (personFan) {
                    personFan.innerHTML = '';
                    
                    let allPhotos = data.top_person_photos || [];
                    
                    // If we have a feature photo, make sure it's in the array
                    if (data.top_person_feature && !allPhotos.includes(data.top_person_feature)) {
                        allPhotos.unshift(data.top_person_feature);
                    }
                    
                    // Limit to 4 photos max for the fan
                    allPhotos = allPhotos.slice(0, 4);
                    
                    if (allPhotos.length > 0) {
                        const angles = allPhotos.length === 4 ? [-18, -6, 6, 18] : allPhotos.length === 3 ? [-12, 0, 12] : allPhotos.length === 2 ? [-8, 8] : [0];
                        const zIndices = [1, 2, 4, 3]; // Feature photo is often at idx 0 or 1, let's just stagger
                        
                        allPhotos.forEach((p, idx) => {
                            const div = document.createElement('div');
                            div.className = 'person-fan-photo';
                            if (p === data.top_person_feature) {
                                div.classList.add('feature-photo');
                                div.style.zIndex = 10;
                                div.style.transform = `rotate(0deg) translateY(0px)`;
                            } else {
                                div.style.zIndex = zIndices[idx] || 1;
                                div.style.transform = `rotate(${angles[idx] || 0}deg) translateX(${angles[idx] * 2}px)`;
                            }
                            div.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(p)}" />`;
                            personFan.appendChild(div);
                        });
                    }
                }
            } else {
                document.getElementById('slide-person').style.display = 'none'; // skip
            }'''

js = js.replace(old_person_block, new_person_block)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated JS for person photos fan!")
