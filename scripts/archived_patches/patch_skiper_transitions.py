import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the boring playSlideTransition with the Skiper-style transitions
old_func_pattern = r"(function playSlideTransition\(callback\) \{.*?)(?=\nfunction nextRecapSlide)"

new_func = '''function playSlideTransition(callback) {
    if (isRecapTransitioning) return;
    isRecapTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'flex';
    layer.style.alignItems = 'center';
    layer.style.justifyContent = 'center';
    layer.style.overflow = 'hidden';
    layer.innerHTML = '';
    layer.style.background = 'transparent';
    
    // We need photos for Skiper transitions. If none, fallback to a fast blur.
    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const types = photos.length >= 3 ? ['skiper-34-scrapbook', 'skiper-32-zoom', 'skiper-33-film'] : ['blur'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    // Helper to get random photo
    const getRandImg = () => `/api/photo/file/${encodeURIComponent(photos[Math.floor(Math.random() * photos.length)])}`;
    
    if (type === 'skiper-34-scrapbook') {
        // Drop 2-3 polaroids fast, scatter out
        const num = 2 + Math.floor(Math.random() * 2);
        let completed = 0;
        
        for(let i=0; i<num; i++) {
            const p = document.createElement('div');
            p.className = 'montage-polaroid';
            p.style.position = 'absolute';
            p.style.width = '35vw';
            p.style.maxWidth = '400px';
            p.innerHTML = `<img src="${getRandImg()}" />`;
            layer.appendChild(p);
            
            setTimeout(() => {
                const rot = (Math.random() * 40 - 20).toFixed(1);
                p.style.transform = `scale(1) translateY(0) rotate(${rot}deg)`;
                p.style.zIndex = i + 10;
                p.classList.add('in');
                
                if (i === num - 1) {
                    // Last one dropped, wait a tiny bit, swap slide, then scatter
                    setTimeout(() => {
                        callback();
                        const allP = layer.querySelectorAll('.montage-polaroid');
                        allP.forEach(card => card.classList.add('out'));
                        
                        setTimeout(() => {
                            layer.style.display = 'none';
                            isRecapTransitioning = false;
                        }, 500);
                    }, 400); // Hold stack
                }
            }, i * 120); // Fast drop
        }
    } 
    else if (type === 'skiper-32-zoom') {
        // A single photo expands to fill screen, slide swaps, then it zooms through the camera
        const p = document.createElement('img');
        p.src = getRandImg();
        p.style.position = 'absolute';
        p.style.width = '20vw';
        p.style.height = '20vh';
        p.style.objectFit = 'cover';
        p.style.borderRadius = '20px';
        p.style.boxShadow = '0 30px 60px rgba(0,0,0,0.5)';
        p.style.transform = 'scale(0.5)';
        p.style.opacity = '0';
        p.style.transition = 'all 0.4s cubic-bezier(0.8, 0, 0.2, 1)';
        layer.appendChild(p);
        
        requestAnimationFrame(() => {
            p.style.transform = 'scale(1)';
            p.style.width = '100vw';
            p.style.height = '100vh';
            p.style.borderRadius = '0px';
            p.style.opacity = '1';
        });
        
        setTimeout(() => {
            callback(); // Swap slide while screen is covered
            p.style.transition = 'all 0.5s cubic-bezier(0.8, 0, 0.2, 1)';
            p.style.transform = 'scale(2.5)'; // Zoom through camera
            p.style.opacity = '0';
            
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 500);
        }, 400);
    }
    else if (type === 'skiper-33-film') {
        // Horizontal film strip sliding across
        const strip = document.createElement('div');
        strip.style.position = 'absolute';
        strip.style.display = 'flex';
        strip.style.gap = '20px';
        strip.style.transform = 'translateX(100vw) rotate(-5deg)';
        strip.style.transition = 'transform 0.6s cubic-bezier(0.7, 0, 0.3, 1)';
        
        for(let i=0; i<3; i++) {
            const img = document.createElement('img');
            img.src = getRandImg();
            img.style.width = '60vw';
            img.style.height = '80vh';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '10px';
            img.style.boxShadow = '0 20px 40px rgba(0,0,0,0.6)';
            strip.appendChild(img);
        }
        layer.appendChild(strip);
        
        requestAnimationFrame(() => {
            strip.style.transform = 'translateX(0) rotate(0deg)'; // Center it
        });
        
        setTimeout(() => {
            callback();
            strip.style.transform = 'translateX(-100vw) rotate(5deg)'; // Slide out
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 600);
        }, 450);
    }
    else {
        // Fallback blur
        layer.style.backdropFilter = 'blur(0px)';
        layer.style.transition = 'backdrop-filter 0.3s ease';
        requestAnimationFrame(() => layer.style.backdropFilter = 'blur(30px)');
        setTimeout(() => {
            callback();
            layer.style.backdropFilter = 'blur(0px)';
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 300);
        }, 300);
    }
}
'''

js = re.sub(old_func_pattern, new_func, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Injected Skiper transitions!")
