import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# We want to replace the ENTIRE playSlideTransition function
# It starts at `function playSlideTransition(callback) {`
# and ends right before `function nextRecapSlide() {`

start_idx = js_code.find("function playSlideTransition(callback) {")
end_idx = js_code.find("function nextRecapSlide() {", start_idx)

new_play_slide = '''function playSlideTransition(callback) {
    if (isRecapTransitioning) return;
    isRecapTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'flex';
    layer.style.alignItems = 'center';
    layer.style.justifyContent = 'center';
    layer.style.overflow = 'hidden';
    layer.innerHTML = '';
    layer.style.background = 'transparent';
    
    const photos = (recapData && recapData.gallery_photos && recapData.gallery_photos.length > 0) 
        ? recapData.gallery_photos 
        : [];
        
    const types = photos.length >= 3 ? ['skiper-32', 'skiper-30', 'skiper-71', 'skiper-33'] : ['blur'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    if (type === 'skiper-32') {
        // Skiper 32 GSAP 3D Grid Reveal
        const grid = document.createElement('div');
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(5, 1fr)';
        grid.style.gap = '10px';
        grid.style.width = '150vw';
        grid.style.height = '150vh';
        grid.style.transform = 'translateZ(-1000px) rotateX(45deg)';
        grid.style.transformStyle = 'preserve-3d';
        grid.style.perspective = '2000px';
        
        for(let i=0; i<20; i++) {
            const img = document.createElement('img');
            img.src = '/api/photo/file/' + encodeURIComponent(photos[i % photos.length]);
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '12px';
            img.style.opacity = '0';
            img.style.transform = `translateZ(${Math.random() * 500 - 250}px)`;
            grid.appendChild(img);
        }
        layer.appendChild(grid);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(grid.children, {
            opacity: 1,
            z: 0,
            duration: 0.8,
            stagger: 0.05,
            ease: "power3.out"
        }, 0);
        
        tl.to(grid, {
            z: 500,
            rotateX: 0,
            duration: 1.5,
            ease: "power3.inOut",
            onUpdate: function() {
                if(this.progress() > 0.5 && callback) {
                    callback();
                    callback = null;
                }
            }
        }, 0);
        
        tl.to(grid.children, {
            opacity: 0,
            z: 500,
            duration: 0.5,
            stagger: 0.02,
            ease: "power2.in"
        }, 1.2);
        
    } else if (type === 'skiper-30') {
        // Skiper 30 GSAP Depth Parallax Blur
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.opacity = '0';
        img.style.transform = 'scale(1)';
        img.style.filter = 'blur(0px)';
        layer.appendChild(img);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(img, {
            opacity: 1,
            scale: 1.5,
            filter: 'blur(30px)',
            duration: 0.8,
            ease: "power3.in",
            onComplete: () => {
                if(callback) { callback(); callback = null; }
            }
        });
        
        tl.to(img, {
            opacity: 0,
            scale: 2,
            duration: 0.8,
            ease: "power3.out"
        });
        
    } else if (type === 'skiper-71') {
        // Skiper 71 GSAP Image Reveal (Clip Path Wipe)
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.clipPath = 'polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%)';
        layer.appendChild(img);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(img, {
            clipPath: 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)',
            duration: 1,
            ease: "expo.inOut",
            onComplete: () => {
                if(callback) { callback(); callback = null; }
            }
        });
        
        tl.to(img, {
            opacity: 0,
            scale: 1.1,
            duration: 0.6,
            ease: "power2.out"
        });
        
    } else if (type === 'skiper-33') {
        // Skiper 33 Framer Perspective Scroll (GSAP 3D Spin)
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '60vw';
        img.style.height = '60vh';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '24px';
        img.style.transform = 'perspective(1000px) rotateY(90deg) scale(0.5)';
        img.style.opacity = '0';
        layer.appendChild(img);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }
        });
        
        tl.to(img, {
            opacity: 1,
            rotateY: 0,
            scale: 1.2,
            duration: 1,
            ease: "back.out(1.7)",
            onComplete: () => {
                if(callback) { callback(); callback = null; }
            }
        });
        
        tl.to(img, {
            opacity: 0,
            rotateY: -90,
            scale: 2,
            duration: 0.8,
            ease: "power3.in"
        });
        
    } else {
        // Fallback Blur
        layer.style.background = 'rgba(0,0,0,0.8)';
        layer.style.opacity = '0';
        gsap.to(layer, {
            opacity: 1,
            duration: 0.4,
            onComplete: () => {
                if (callback) callback();
                gsap.to(layer, {
                    opacity: 0,
                    duration: 0.4,
                    onComplete: () => {
                        layer.style.display = 'none';
                        isRecapTransitioning = false;
                    }
                });
            }
        });
    }
}
'''

js_code = js_code[:start_idx] + new_play_slide + js_code[end_idx:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Injected Skiper GSAP transitions")
