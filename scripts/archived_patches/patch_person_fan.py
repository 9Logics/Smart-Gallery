import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

person_logic = '''
            document.getElementById('recap-stat-person').innerText = data.top_person || "Yourself!";
            
            // Render Person Fan Photos
            const personFan = document.getElementById('person-photos-fan');
            if (personFan) {
                personFan.innerHTML = '';
                
                let pPhotos = data.top_person_photos || [];
                const feat = data.top_person_feature;
                
                // Add feature photo to the center (if available)
                let fanPhotos = [];
                if (feat) {
                    fanPhotos.push(feat);
                }
                // Fill the rest up to 5 total photos
                for (let i = 0; i < pPhotos.length; i++) {
                    if (fanPhotos.length >= 5) break;
                    if (pPhotos[i] !== feat) {
                        fanPhotos.push(pPhotos[i]);
                    }
                }
                
                if (fanPhotos.length > 0) {
                    // Create polaroid style fan
                    const angles = fanPhotos.length === 5 ? [-20, -10, 0, 10, 20] :
                                   fanPhotos.length === 4 ? [-15, -5, 5, 15] :
                                   fanPhotos.length === 3 ? [-12, 0, 12] :
                                   fanPhotos.length === 2 ? [-8, 8] : [0];
                    
                    fanPhotos.forEach((p, idx) => {
                        const div = document.createElement('div');
                        // Make the feature photo (index 0) stand out more if we have multiple
                        const isFeature = (feat && p === feat);
                        div.className = isFeature ? 'person-fan-photo feature-photo' : 'person-fan-photo';
                        
                        // Feature photo stays on top
                        const z = isFeature ? 10 : (5 - Math.abs(angles[idx]));
                        
                        // Push outer photos down slightly to create an arc
                        const dropY = Math.abs(angles[idx] || 0) * 1.5;
                        
                        div.style.zIndex = z;
                        div.style.transform = `rotate(${angles[idx] || 0}deg) translateY(${dropY}px)`;
                        div.innerHTML = `<img src="/api/photo/thumbnail/${encodeURIComponent(p)}" />`;
                        personFan.appendChild(div);
                    });
                }
            }
'''

js = js.replace("document.getElementById('recap-stat-person').innerText = data.top_person || \"Yourself!\";", person_logic)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Added person-fan-photo generation logic.")
