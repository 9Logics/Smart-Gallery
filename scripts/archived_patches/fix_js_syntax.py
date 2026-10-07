import re
js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js_code = f.read()

pattern = re.compile(r"const heroContainer = document\.getElementById\('hero-moment-container'\);.*?heroContainer\.innerHTML \+= `<img src.*?}\n                }", re.DOTALL)

replacement = '''const heroContainer = document.getElementById('hero-moment-container');
                if (heroContainer) {
                    heroContainer.innerHTML = '';
                    const mPhotos = data.moment_photos && data.moment_photos.length > 0 ? data.moment_photos : (data.memorable_moment ? [data.memorable_moment] : []);
                    
                    heroContainer.style.display = 'flex';
                    heroContainer.style.justifyContent = 'center';
                    heroContainer.style.alignItems = 'center';
                    heroContainer.style.position = 'relative';
                    heroContainer.style.height = '50vh';
                    heroContainer.style.width = '100vw';
                    heroContainer.classList.remove('hero-glow-border');

                    const rotations = [-4, 5, -2, 3];
                    const zIndexes = [10, 11, 12, 13];
                    const offsetsX = [-10, 10, -5, 5]; // vw
                    const offsetsY = [-2, 5, -5, 2];   // vh

                    mPhotos.slice(0, 4).forEach((photoPath, idx) => {
                        const wrapper = document.createElement('div');
                        wrapper.className = 'hero-scrapbook-photo';
                        
                        if (mPhotos.length > 1) {
                            wrapper.style.position = 'absolute';
                            wrapper.style.transform = `translate(${offsetsX[idx] || 0}vw, ${offsetsY[idx] || 0}vh) rotate(${rotations[idx] || 0}deg)`;
                            wrapper.style.zIndex = zIndexes[idx] || 10;
                        } else {
                            wrapper.style.transform = `rotate(-2deg)`;
                        }

                        const img = document.createElement('img');
                        img.src = `/api/photo/file/${encodeURIComponent(photoPath)}`;
                        wrapper.appendChild(img);
                        heroContainer.appendChild(wrapper);
                    });
                }'''

new_js, count = pattern.subn(replacement, js_code)
if count > 0:
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_js)
    print(f'Patched JS {count} times!')
else:
    print('Failed to patch JS')
