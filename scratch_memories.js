// Write a script to replace the hero logic in memories.js
import fs from 'fs';

const filePath = 'static/js/views/memories.js';
let text = fs.readFileSync(filePath, 'utf8');

const target = \            const btn = document.getElementById('hero-lightbox-btn');
            if (btn) {
                btn.onclick = (e) => {
                    e.stopPropagation();
                    if (typeof state !== 'undefined') {
                        state.lightboxPhotos = photos.map(p => ({
                            path: p.path,
                            date_taken: p.date_taken,
                            file_type: p.file_type || (p.path.match(/\\.(mp4|mov|avi|mkv|webm)$/i) ? 'MP4' : 'JPG')
                        }));
                    }
                    if (typeof openLightbox === 'function') openLightbox(photo.path);
                };
            }
        };

        if (photos.length > 0) updateHeroMetadata(photos[0]);

        if (heroInterval) clearInterval(heroInterval);
        if (imgDivs.length > 1) {
            let curr = 0;
            
            const cycleNext = () => {
                imgDivs[curr].classList.remove('active');
                curr = (curr + 1) % imgDivs.length;
                imgDivs[curr].classList.add('active');
                updateHeroMetadata(photos[curr]);
            };
            
            heroInterval = setInterval(cycleNext, 10000);
            
            // Dislike button
            const btnDislike = document.getElementById('hero-dislike-btn');
            if (btnDislike) {
                btnDislike.onclick = (e) => {
                    e.stopPropagation();
                    fetch('/api/memories/hero/blacklist', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({path: photos[curr].path})
                    });
                    
                    // Remove from arrays so it doesn't show again in this session
                    imgDivs[curr].remove();
                    imgDivs.splice(curr, 1);
                    photos.splice(curr, 1);
                    if(curr >= imgDivs.length) curr = 0;
                    
                    if (imgDivs.length > 0) {
                        imgDivs[curr].classList.add('active');
                        updateHeroMetadata(photos[curr]);
                        clearInterval(heroInterval);
                        heroInterval = setInterval(cycleNext, 10000);
                    }
                };
            }
            
            // Scan more button
            const btnScanMore = document.getElementById('hero-scan-more-btn');
            if (btnScanMore) {
                btnScanMore.onclick = (e) => {
                    e.stopPropagation();
                    const icon = btnScanMore.querySelector('i');
                    if (icon) {
                        icon.style.transition = 'transform 1s linear';
                        icon.style.transform = 'rotate(360deg)';
                        setTimeout(() => { icon.style.transition = ''; icon.style.transform = ''; }, 1000);
                    }
                    fetch('/api/memories/hero/scan_more', { method: 'POST' });
                    cycleNext();
                    clearInterval(heroInterval);
                    heroInterval = setInterval(cycleNext, 10000);
                };
            }
            
            window.memoriesCleanups.push(() => {
                if (heroInterval) clearInterval(heroInterval);
            });
        }
\;

const oldTarget = \            const btn = document.getElementById('hero-lightbox-btn');
            if (btn) {
                btn.onclick = (e) => {
                    e.stopPropagation();
                    if (typeof state !== 'undefined') {
                        state.lightboxPhotos = photos.map(p => ({
                            path: p.path,
                            date_taken: p.date_taken,
                            file_type: p.file_type || (p.path.match(/\\.(mp4|mov|avi|mkv|webm)$/i) ? 'MP4' : 'JPG')
                        }));
                    }
                    if (typeof openLightbox === 'function') openLightbox(photo.path);
                };
            }
        };

        if (photos.length > 0) updateHeroMetadata(photos[0]);

        if (heroInterval) clearInterval(heroInterval);
        if (imgDivs.length > 1) {
            let curr = 0;
            heroInterval = setInterval(() => {
                imgDivs[curr].classList.remove('active');
                curr = (curr + 1) % imgDivs.length;
                imgDivs[curr].classList.add('active');
                updateHeroMetadata(photos[curr]);
            }, 10000);
            
            window.memoriesCleanups.push(() => {
                if (heroInterval) clearInterval(heroInterval);
            });
        }\;

text = text.replace(oldTarget, target);
fs.writeFileSync(filePath, text);
