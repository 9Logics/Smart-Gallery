import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_gallery = '''            // Skiper 30 Parallax Gallery
            const gallery = document.getElementById('recap-parallax-gallery');
            gallery.innerHTML = '';
            if (data.gallery_photos && data.gallery_photos.length > 0) {
                data.gallery_photos.forEach((photoPath, i) => {
                    if(i > 4) return; // Limit to 5 background photos
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item p-item-${i+1}`;
                    gallery.appendChild(img);
                });
            }'''

new_gallery = '''            // Skiper 30 Parallax Gallery - Massive Scatter
            const gallery = document.getElementById('recap-parallax-gallery');
            gallery.innerHTML = '';
            
            // Clean up any previously injected dynamic styles
            document.querySelectorAll('.dynamic-float-style').forEach(el => el.remove());
            
            if (data.gallery_photos && data.gallery_photos.length > 0) {
                let shuffled = [...data.gallery_photos].sort(() => 0.5 - Math.random());
                
                shuffled.forEach((photoPath, i) => {
                    if(i > 15) return; // Limit to 16 background photos to completely fill screen
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item`;
                    
                    const size = 150 + Math.random() * 250; 
                    const posX = Math.random() * 85; 
                    const posY = Math.random() * 85; 
                    const delay = Math.random() * -30; 
                    const duration = 20 + Math.random() * 20; 
                    const rot = (Math.random() - 0.5) * 50; 
                    
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*80 - 40)}px`;
                    img.style.left = `${posX}vw`;
                    img.style.top = `${posY}vh`;
                    img.style.opacity = '0.35';
                    img.style.zIndex = Math.floor(Math.random() * 10);
                    
                    const animName = `customFloat${i}_${Date.now()}`;
                    const style = document.createElement('style');
                    style.className = 'dynamic-float-style';
                    style.innerHTML = `
                        @keyframes ${animName} {
                            0% { transform: translateY(0px) rotate(${rot}deg); }
                            100% { transform: translateY(${Math.random()*300 - 150}px) rotate(${rot + (Math.random()*30-15)}deg); }
                        }
                    `;
                    document.head.appendChild(style);
                    
                    img.style.animation = `${animName} ${duration}s infinite alternate ease-in-out`;
                    img.style.animationDelay = `${delay}s`;
                    
                    gallery.appendChild(img);
                });
            }'''

js = js.replace(old_gallery, new_gallery)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated JS for massive parallax gallery scatter!")
