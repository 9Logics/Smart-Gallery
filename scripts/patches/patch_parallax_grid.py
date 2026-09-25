import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# I will replace the previous scatter logic block entirely.
old_scatter_pattern = r"if \(data\.gallery_photos && data\.gallery_photos\.length > 0\) \{.*?let shuffled = \[\.\.\.data\.gallery_photos\]\.sort\(\(\) => 0\.5 - Math\.random\(\)\);.*?shuffled\.forEach\(\(photoPath, i\) => \{.*?gallery\.appendChild\(img\);\n                \}\);\n            \}"

new_scatter = '''if (data.gallery_photos && data.gallery_photos.length > 0) {
                // Ensure we have a large enough pool to fill the screen even if the year has few photos
                let pool = [...data.gallery_photos];
                while(pool.length < 24) {
                    pool = pool.concat(data.gallery_photos);
                }
                pool.sort(() => 0.5 - Math.random());
                
                // Use a Grid-based scatter (6 cols x 4 rows = 24 cells) to prevent clumps and collisions
                let renderList = pool.slice(0, 24);
                let idx = 0;
                
                for (let row = 0; row < 4; row++) {
                    for (let col = 0; col < 6; col++) {
                        if(idx >= renderList.length) break;
                        
                        const img = document.createElement('img');
                        img.src = `/api/photo/thumbnail/${encodeURIComponent(renderList[idx])}`;
                        img.className = `parallax-gallery-item`;
                        
                        const size = 150 + Math.random() * 180; 
                        
                        // Map to the visible 10% - 90% of the oversized container to ensure they are on screen
                        // 80% / 6 cols = 13.3% wide cells. 80% / 4 rows = 20% high cells.
                        const cellX = 10 + (col * 13.3); 
                        const cellY = 10 + (row * 20);
                        
                        // Add jitter inside the cell
                        const posX = cellX + (Math.random() * 6 - 3); 
                        const posY = cellY + (Math.random() * 10 - 5); 
                        
                        const delay = Math.random() * -30; 
                        const duration = 25 + Math.random() * 20; 
                        const rot = (Math.random() - 0.5) * 50; 
                        
                        img.style.position = 'absolute';
                        img.style.width = `${size}px`;
                        img.style.height = `${size + (Math.random()*60 - 30)}px`;
                        img.style.left = `${posX}%`;
                        img.style.top = `${posY}%`;
                        img.style.opacity = '0.35';
                        img.style.zIndex = Math.floor(Math.random() * 10);
                        
                        const animName = `customFloat${idx}_${Date.now()}`;
                        const style = document.createElement('style');
                        style.className = 'dynamic-float-style';
                        style.innerHTML = `
                            @keyframes ${animName} {
                                0% { transform: translateY(0px) rotate(${rot}deg); }
                                100% { transform: translateY(${Math.random()*150 - 75}px) rotate(${rot + (Math.random()*20-10)}deg); }
                            }
                        `;
                        document.head.appendChild(style);
                        
                        img.style.animation = `${animName} ${duration}s infinite alternate ease-in-out`;
                        img.style.animationDelay = `${delay}s`;
                        
                        gallery.appendChild(img);
                        idx++;
                    }
                }
            }'''

js = re.sub(old_scatter_pattern, new_scatter, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated JS scatter logic with guaranteed grid distribution!")
