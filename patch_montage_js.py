import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_show = '''function showRecapSlide(index) {
    recapSlides.forEach((s, i) => {
        if (i === index) {
            s.classList.add('active');
            
            // If it's the stats slide, trigger number animation (Skiper 37)
            if (s.id === 'slide-stats' && recapData) {
                const p = document.getElementById('recap-stat-photos');
                const v = document.getElementById('recap-stat-videos');
                p.innerHTML = '0';
                v.innerHTML = '0';
                setTimeout(() => {
                    animateNumberFlow(p, 0, recapData.total_photos, 2000);
                    animateNumberFlow(v, 0, recapData.total_videos, 2000);
                }, 300);
            }
            
        } else {
            s.classList.remove('active');
        }
    });
}'''

new_show = '''function showRecapSlide(index) {
    recapSlides.forEach((s, i) => {
        if (i === index) {
            s.classList.add('active');
            
            // Montage Transition Buffer Slide
            if (s.id === 'slide-montage' && recapData) {
                const container = document.getElementById('montage-container');
                container.innerHTML = '';
                
                if (recapData.gallery_photos && recapData.gallery_photos.length > 0) {
                    const photos = recapData.gallery_photos.slice(0, 5); // Max 5 polaroids
                    
                    photos.forEach((photoPath, idx) => {
                        const polaroid = document.createElement('div');
                        polaroid.className = 'montage-polaroid';
                        polaroid.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(photoPath)}" />`;
                        container.appendChild(polaroid);
                        
                        // Stagger entrance
                        setTimeout(() => {
                            // Calculate random rotation between -15 and 15 degrees
                            const rotation = (Math.random() * 30 - 15).toFixed(1);
                            polaroid.style.transform = `scale(1) translateY(0) rotate(${rotation}deg)`;
                            polaroid.style.zIndex = idx + 10;
                            polaroid.classList.add('in');
                            
                            // If this is the last polaroid, trigger the exit and next slide
                            if (idx === photos.length - 1) {
                                setTimeout(() => {
                                    // Scatter out
                                    const allPolaroids = container.querySelectorAll('.montage-polaroid');
                                    allPolaroids.forEach(p => p.classList.add('out'));
                                    
                                    // Auto-advance to intro text slide
                                    setTimeout(() => {
                                        nextRecapSlide();
                                    }, 600); // Wait for scatter animation
                                }, 1500); // Hold the final stacked montage for 1.5s
                            }
                        }, idx * 180); // 180ms delay between drops
                    });
                } else {
                    // Skip montage if no photos
                    setTimeout(nextRecapSlide, 50);
                }
            }
            
            // If it's the stats slide, trigger number animation (Skiper 37)
            if (s.id === 'slide-stats' && recapData) {
                const p = document.getElementById('recap-stat-photos');
                const v = document.getElementById('recap-stat-videos');
                p.innerHTML = '0';
                v.innerHTML = '0';
                setTimeout(() => {
                    animateNumberFlow(p, 0, recapData.total_photos, 2000);
                    animateNumberFlow(v, 0, recapData.total_videos, 2000);
                }, 300);
            }
            
        } else {
            s.classList.remove('active');
        }
    });
}'''

js = js.replace(old_show, new_show)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Added montage JS logic!")
