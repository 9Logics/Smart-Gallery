import re
import os

# 1. Fix app/routes/photos.py (A3)
photos_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\routes\photos.py"
with open(photos_path, "r", encoding="utf-8") as f:
    py_code = f.read()

# Change LIMIT 6 to LIMIT 30
py_code = py_code.replace("ORDER BY RANDOM() LIMIT 6", "ORDER BY RANDOM() LIMIT 30")
with open(photos_path, "w", encoding="utf-8") as f:
    f.write(py_code)


# 2. Fix app/static/js/recap_player.js (A1 & C)
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# A1 Fix: Memory Leak in closeRecapPlayer
old_close = "function closeRecapPlayer() {"
new_close = '''function closeRecapPlayer() {
    if (window.recapDeckIntervals) {
        window.recapDeckIntervals.forEach(clearInterval);
        window.recapDeckIntervals = [];
    }'''
if "window.recapDeckIntervals.forEach" not in js_code:
    js_code = js_code.replace(old_close, new_close)

# C1, C2, C3 Fix: Parallax Background Overhaul
old_scatter = r"if \(data\.gallery_photos && data\.gallery_photos\.length > 0\) \{.*?pool\.sort\(\(\) => 0\.5 - Math\.random\(\)\);.*?let renderList = pool\.slice\(0, 24\);.*?gallery\.appendChild\(img\);\n\s+\}\);\n\s+\}"

new_scatter = '''if (data.gallery_photos && data.gallery_photos.length > 0) {
                let pool = [...new Set(data.gallery_photos)];
                pool.sort(() => 0.5 - Math.random());
                
                // Allow up to 24 photos. If fewer, allow duplication up to 24 to fill space.
                let renderList = [];
                while (renderList.length < 24 && pool.length > 0) {
                    renderList = renderList.concat(pool);
                }
                renderList = renderList.slice(0, 24);
                
                let slots = [];
                for (let i = 0; i < 24; i++) slots.push(i);
                slots.sort(() => 0.5 - Math.random());
                
                renderList.forEach((photoPath, i) => {
                    const slot = slots[i];
                    const col = slot % 6;
                    const row = Math.floor(slot / 6);
                    
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item`;
                    
                    // C1: 3 Size Tiers
                    const sizeTier = Math.random();
                    const size = sizeTier > 0.8 ? (200 + Math.random()*40) : sizeTier > 0.4 ? (140 + Math.random()*40) : (80 + Math.random()*40);
                    
                    const cellX = 15 + (col * 11.6); 
                    const cellY = 15 + (row * 17.5);
                    const posX = cellX + (Math.random() * 4 - 2); 
                    const posY = cellY + (Math.random() * 4 - 2); 
                    
                    const delay = Math.random() * -30; 
                    const duration = 25 + Math.random() * 20; 
                    
                    // C2: Depth-Aware Opacity & Blur
                    const depthTier = Math.random();
                    let opacity = 0.3;
                    let blur = 0;
                    let scale = 1;
                    
                    if (depthTier > 0.6) {
                        opacity = 0.45; scale = 1.1; // Near
                    } else if (depthTier > 0.3) {
                        opacity = 0.30; // Mid
                    } else {
                        opacity = 0.15; blur = 2; // Far
                    }
                    
                    img.style.position = 'absolute';
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*40 - 20)}px`;
                    img.style.left = `${posX}%`;
                    img.style.top = `${posY}%`;
                    img.style.opacity = opacity;
                    img.style.filter = `blur(${blur}px)`;
                    img.style.transform = `scale(${scale})`;
                    img.style.zIndex = Math.floor(Math.random() * 5);
                    
                    const animName = `customFloat${i}_${Date.now()}`;
                    const style = document.createElement('style');
                    style.className = 'dynamic-float-style';
                    
                    // C3: Smooth Continuous Float (Elliptical multi-waypoint)
                    const rotBase = (Math.random() - 0.5) * 40;
                    const driftY = 40 + Math.random() * 40;
                    const driftX = 20 + Math.random() * 20;
                    
                    style.innerHTML = `
                        @keyframes ${animName} {
                            0% { transform: translate(0px, 0px) rotate(${rotBase}deg) scale(${scale}); }
                            33% { transform: translate(${driftX}px, ${driftY}px) rotate(${rotBase + 5}deg) scale(${scale}); }
                            66% { transform: translate(${-driftX}px, ${driftY*1.2}px) rotate(${rotBase - 5}deg) scale(${scale}); }
                            100% { transform: translate(0px, 0px) rotate(${rotBase}deg) scale(${scale}); }
                        }
                    `;
                    document.head.appendChild(style);
                    
                    img.style.animation = `${animName} ${duration}s infinite linear`;
                    img.style.animationDelay = `${delay}s`;
                    
                    gallery.appendChild(img);
                });
            }'''

js_code = re.sub(old_scatter, new_scatter, js_code, flags=re.DOTALL)
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)


# 3. Fix app/templates/index.html (A2 & B2)
html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

old_hero_loop = r'''// Step 1: Set instant synchronous fallbacks
                                  let heroImages = \[\];
                                  let attempts = 0;
                                  while\(heroImages\.length < 3 && attempts < 20\) \{
                                      heroImages\.push\('data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='\);
                                      attempts\+\+;
                                  \}
                                  
                                  heroImages\.forEach\(\(src, idx\) => \{
                                      let div = document\.createElement\('div'\);
                                      div\.className = `hero-collage-item hero-collage-\$\{idx\+1\}`;
                                      if\(src\) div\.style\.backgroundImage = `url\('\$\{src\}'\)`;
                                      heroContainer\.appendChild\(div\);
                                  \}\);'''

new_hero_loop = '''// A2 Fix: Wait for async fetch to populate hero collage
                                  // (Synchronous fallback removed)'''
html_code = re.sub(old_hero_loop, new_hero_loop, html_code, flags=re.DOTALL)

old_hero_fetch = r'''// Shuffle array
                                              photos\.sort\(\(\) => 0\.5 - Math\.random\(\)\);
                                              document\.querySelectorAll\('\.hero-collage-item'\)\.forEach\(\(div, idx\) => \{
                                                  // We use /thumbnail/ to load fast, or /file/ for high-res\. 
                                                  // The hero is large, so let's use the file API but let it load naturally
                                                  div\.style\.backgroundImage = `url\('/api/photo/thumbnail/\$\{encodeURIComponent\(photos\[idx\]\.path\)\}'\)`;
                                              \}\);'''

new_hero_fetch = '''// Shuffle array
                                              photos.sort(() => 0.5 - Math.random());
                                              heroContainer.innerHTML = ''; // Clear container
                                              
                                              for (let idx = 0; idx < Math.min(3, photos.length); idx++) {
                                                  let div = document.createElement('div');
                                                  div.className = `hero-collage-item hero-collage-${idx+1}`;
                                                  div.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(photos[idx].path)}')`;
                                                  heroContainer.appendChild(div);
                                              }
                                              
                                              // B2: Hover tilt effect for Hero Card
                                              const heroCardElement = document.getElementById('rewind-hero-card');
                                              heroCardElement.addEventListener('mousemove', (e) => {
                                                  const rect = heroCardElement.getBoundingClientRect();
                                                  const x = e.clientX - rect.left;
                                                  const y = e.clientY - rect.top;
                                                  const cx = rect.width / 2;
                                                  const cy = rect.height / 2;
                                                  const tiltX = (y - cy) / cy * -5; // max 5deg
                                                  const tiltY = (x - cx) / cx * 5;
                                                  heroContainer.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale(1.02)`;
                                              });
                                              heroCardElement.addEventListener('mouseleave', () => {
                                                  heroContainer.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)`;
                                              });'''

html_code = re.sub(old_hero_fetch, new_hero_fetch, html_code, flags=re.DOTALL)
html_code = html_code.replace("v=312", "v=313")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print("Applied Phase A (Bug Fixes) and Phase C (Parallax). Modified photos.py, recap_player.js, and index.html.")
