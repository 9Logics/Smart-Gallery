import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''                                // Smart Thumbnail Assignment
                                const photoCards = Array.from(document.querySelectorAll('.photo-card'));
                                const gallery = photoCards.map(c => c.querySelector('img')?.src).filter(Boolean);
                                
                                const getBestImage = (keyword, seed) => {
                                    // 1. Check if user's gallery has an image matching the month/year text
                                    const match = photoCards.find(card => card.innerText.includes(keyword));
                                    if (match && match.querySelector('img')) return match.querySelector('img').src;
                                    // 2. Fallback to random user photo
                                    if (gallery.length > 0) return gallery[Math.floor(Math.random() * gallery.length)];
                                    // 3. Fallback to high-quality seeded stock photo
                                    return `https://picsum.photos/seed/${seed}/800/600`;
                                };'''

new_js = '''                                // Bulletproof Smart Thumbnail Assignment
                                let galleryPhotos = [];
                                document.querySelectorAll('img').forEach(img => {
                                    if (img.src && img.src.includes('/api/photo')) galleryPhotos.push(img.src);
                                });
                                document.querySelectorAll('.hero-bg-img, .memory-card, .album-card').forEach(el => {
                                    let bg = el.style.backgroundImage;
                                    if (bg && bg.includes('url')) {
                                        let url = bg.replace(/^url\\(['"]?/, '').replace(/['"]?\\)$/, '');
                                        if (url.includes('/api/photo')) galleryPhotos.push(url);
                                    }
                                });
                                galleryPhotos = [...new Set(galleryPhotos)];
                                
                                const getBestImage = (keyword, seed) => {
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
                                };'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=267', 'v=268')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS for Bulletproof Thumbnails!")
else:
    print("Could not find JS block to replace!")
