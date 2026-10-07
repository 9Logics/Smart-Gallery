import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# We need to replace the block starting at if (heroContainer) { up to // Finish loader
old_pattern = r"if \(heroContainer\) \{.*?(?=// Finish loader)"
# We will use re.DOTALL to match across newlines
match = re.search(old_pattern, js, flags=re.DOTALL)
if match:
    old_code = match.group(0)
    
    new_code = '''if (heroContainer) {
                    heroContainer.innerHTML = '';
                    const mPhotos = data.moment_photos && data.moment_photos.length > 0 ? data.moment_photos : (data.memorable_moment ? [data.memorable_moment] : []);
                    
                    heroContainer.style.display = 'block';
                    heroContainer.style.marginTop = '20px';
                    heroContainer.classList.remove('hero-glow-border');

                    if (mPhotos.length > 0) {
                        // Create Wrapper
                        const wrapper = document.createElement('div');
                        wrapper.className = 'hero-marquee-wrapper';
                        
                        // Split photos into two rows
                        const row1Photos = [];
                        const row2Photos = [];
                        
                        // We want enough photos to fill a long row, so if we only have a few, duplicate them
                        let pool = [...mPhotos];
                        while(pool.length < 20) {
                            pool = pool.concat(mPhotos);
                        }
                        
                        pool.forEach((p, idx) => {
                            if (idx % 2 === 0) row1Photos.push(p);
                            else row2Photos.push(p);
                        });
                        
                        // Build Row 1 (Left)
                        const row1 = document.createElement('div');
                        row1.className = 'hero-marquee-row left';
                        const buildImages = (photosList) => {
                            let html = '';
                            // Double it for seamless infinite scroll
                            const seamless = photosList.concat(photosList);
                            seamless.forEach(p => {
                                html += <div class="hero-marquee-photo"><img src="/api/photo/file/" loading="lazy" /></div>;
                            });
                            return html;
                        };
                        row1.innerHTML = buildImages(row1Photos);
                        
                        // Build Row 2 (Right)
                        const row2 = document.createElement('div');
                        row2.className = 'hero-marquee-row right';
                        row2.innerHTML = buildImages(row2Photos);
                        
                        wrapper.appendChild(row1);
                        wrapper.appendChild(row2);
                        heroContainer.appendChild(wrapper);
                    }
                }
            
            '''
    
    js = js.replace(old_code, new_code)
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched recap_player.js for hero marquee!")
else:
    print("Could not find the target block in recap_player.js")
