import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''                                const getBestImage = (keyword, seed) => {
                                    const allCards = Array.from(document.querySelectorAll('.photo-card, .album-card, .memory-card'));
                                    const match = allCards.find(card => card.innerText && card.innerText.includes(keyword));
                                    if (match) {
                                        let img = match.querySelector('img');
                                        if (img && img.src.includes('/api/photo')) return img.src;
                                        let bg = match.style.backgroundImage;
                                        if (bg && bg.includes('url')) {
                                            return bg.replace(/^url\\(['"]?/, '').replace(/['"]?\\)$/, '');
                                        }
                                    }
                                    if (galleryPhotos.length > 0) return galleryPhotos[Math.floor(Math.random() * galleryPhotos.length)];
                                    return `https://picsum.photos/seed/${seed}/800/600`;
                                };
                                
                                const heroContainer = document.getElementById('hero-bg-container');
                                heroContainer.innerHTML = '';
                                
                                // Pick 3 unique images for the blended collage if possible
                                let heroImages = [];
                                let attempts = 0;
                                while(heroImages.length < 3 && attempts < 20) {
                                    let candidate = galleryPhotos.length > 0 ? galleryPhotos[Math.floor(Math.random() * galleryPhotos.length)] : `https://picsum.photos/seed/hero${attempts}/800/600`;
                                    if (!heroImages.includes(candidate)) heroImages.push(candidate);
                                    attempts++;
                                }
                                // Fallback to duplicates if gallery is too small
                                while(heroImages.length < 3) heroImages.push(heroImages[0]);
                                
                                heroImages.forEach((src, idx) => {
                                    let div = document.createElement('div');
                                    div.className = `hero-collage-item hero-collage-${idx+1}`;
                                    div.style.backgroundImage = `url('${src}')`;
                                    heroContainer.appendChild(div);
                                });
                                
                                document.querySelectorAll('.rewind-mini-card').forEach(card => {
                                    const overlayText = card.querySelector('.mini-overlay').innerText;
                                    card.querySelector('img').src = getBestImage(overlayText, overlayText);
                                });'''

new_js = '''                                const getBestImage = (keyword, seed) => {
                                    const allCards = Array.from(document.querySelectorAll('.photo-card, .album-card, .memory-card'));
                                    const match = allCards.find(card => card.innerText && card.innerText.includes(keyword));
                                    if (match) {
                                        let img = match.querySelector('img');
                                        if (img && img.src.includes('/api/photo')) return img.src;
                                        let bg = match.style.backgroundImage;
                                        if (bg && bg.includes('url')) {
                                            return bg.replace(/^url\\(['"]?/, '').replace(/['"]?\\)$/, '');
                                        }
                                    }
                                    if (galleryPhotos.length > 0) return galleryPhotos[Math.floor(Math.random() * galleryPhotos.length)];
                                    return `https://picsum.photos/seed/${seed}/800/600`;
                                };
                                
                                const heroContainer = document.getElementById('hero-bg-container');
                                heroContainer.innerHTML = '';
                                
                                // Step 1: Set instant synchronous fallbacks
                                let heroImages = [];
                                let attempts = 0;
                                while(heroImages.length < 3 && attempts < 20) {
                                    let candidate = galleryPhotos.length > 0 ? galleryPhotos[Math.floor(Math.random() * galleryPhotos.length)] : `https://picsum.photos/seed/hero${attempts}/800/600`;
                                    if (!heroImages.includes(candidate)) heroImages.push(candidate);
                                    attempts++;
                                }
                                while(heroImages.length < 3) heroImages.push(heroImages[0]);
                                
                                heroImages.forEach((src, idx) => {
                                    let div = document.createElement('div');
                                    div.className = `hero-collage-item hero-collage-${idx+1}`;
                                    div.style.backgroundImage = `url('${src}')`;
                                    heroContainer.appendChild(div);
                                });
                                
                                document.querySelectorAll('.rewind-mini-card').forEach(card => {
                                    const overlayText = card.querySelector('.mini-overlay').innerText;
                                    card.querySelector('img').src = getBestImage(overlayText, overlayText);
                                    
                                    // Step 2: Asynchronously fetch true photos for this exact month/year!
                                    fetch('/api/photos?date_query=' + encodeURIComponent(overlayText))
                                        .then(res => res.json())
                                        .then(photos => {
                                            if (photos && photos.length > 0) {
                                                let randomPhoto = photos[Math.floor(Math.random() * photos.length)];
                                                card.querySelector('img').src = '/api/photo/thumbnail/' + encodeURIComponent(randomPhoto.path);
                                            }
                                        }).catch(err => console.log('Rewind API fetch failed:', err));
                                });
                                
                                // Fetch true photos for the Hero Collage (2026 Recap)
                                fetch('/api/photos?date_query=2026')
                                    .then(res => res.json())
                                    .then(photos => {
                                        if (photos && photos.length >= 3) {
                                            // Shuffle array
                                            photos.sort(() => 0.5 - Math.random());
                                            document.querySelectorAll('.hero-collage-item').forEach((div, idx) => {
                                                // We use /thumbnail/ to load fast, or /file/ for high-res. 
                                                // The hero is large, so let's use the file API but let it load naturally
                                                div.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(photos[idx].path)}')`;
                                            });
                                        }
                                    }).catch(err => console.log('Hero API fetch failed:', err));'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=269', 'v=270')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS for True Backend Matching!")
else:
    print("Could not find JS block to replace!")
