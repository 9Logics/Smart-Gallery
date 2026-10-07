import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the previous scatter logic
old_scatter_pattern = r"if \(data\.gallery_photos && data\.gallery_photos\.length > 0\) \{.*?let pool = \[\.\.\.data\.gallery_photos\];.*?gallery\.appendChild\(img\);\n                        idx\+\+;\n                    \}\n                \}\n            \}"

new_scatter = '''if (data.gallery_photos && data.gallery_photos.length > 0) {
                // Prevent repeating: cap the pool strictly to unique photos, max 24.
                let pool = [...new Set(data.gallery_photos)]; // Unique only
                pool.sort(() => 0.5 - Math.random());
                
                let renderList = pool.slice(0, 24);
                const count = renderList.length;
                
                // We have a 6x4 grid (24 slots). Pick 'count' random unique slots.
                let slots = [];
                for (let i = 0; i < 24; i++) slots.push(i);
                slots.sort(() => 0.5 - Math.random());
                slots = slots.slice(0, count);
                
                renderList.forEach((photoPath, i) => {
                    const slot = slots[i];
                    const col = slot % 6;
                    const row = Math.floor(slot / 6);
                    
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item`;
                    
                    // Decrease size significantly to prevent overlapping (80px to 220px)
                    const size = 80 + Math.random() * 140; 
                    
                    // Container is 140% oversized. Visible area is ~15% to 85%.
                    // 6 cols spanning 70% = 11.6% width each.
                    // 4 rows spanning 70% = 17.5% height each.
                    const cellX = 15 + (col * 11.6); 
                    const cellY = 15 + (row * 17.5);
                    
                    // Mild jitter to keep them safely inside their cells
                    const posX = cellX + (Math.random() * 4 - 2); 
                    const posY = cellY + (Math.random() * 4 - 2); 
                    
                    const delay = Math.random() * -30; 
                    const duration = 25 + Math.random() * 20; 
                    const rot = (Math.random() - 0.5) * 40; 
                    
                    img.style.position = 'absolute';
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*40 - 20)}px`;
                    img.style.left = `${posX}%`;
                    img.style.top = `${posY}%`;
                    img.style.opacity = '0.35';
                    img.style.zIndex = Math.floor(Math.random() * 10);
                    
                    const animName = `customFloat${i}_${Date.now()}`;
                    const style = document.createElement('style');
                    style.className = 'dynamic-float-style';
                    
                    // Reduce animation drift distance to prevent them floating into each other's spaces
                    style.innerHTML = `
                        @keyframes ${animName} {
                            0% { transform: translateY(0px) rotate(${rot}deg); }
                            100% { transform: translateY(${Math.random()*80 - 40}px) rotate(${rot + (Math.random()*16-8)}deg); }
                        }
                    `;
                    document.head.appendChild(style);
                    
                    img.style.animation = `${animName} ${duration}s infinite alternate ease-in-out`;
                    img.style.animationDelay = `${delay}s`;
                    
                    gallery.appendChild(img);
                });
            }'''

js = re.sub(old_scatter_pattern, new_scatter, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated JS scatter logic to prevent repeating and reduce overlap!")
