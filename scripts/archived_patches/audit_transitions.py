import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# 1. Un-hardcode the transition type
js_code = js_code.replace("const type = 'skiper-33'; // Forced for review", "const type = types[Math.floor(Math.random() * types.length)]; // Dynamic")

# 2. Add layer.innerHTML = ''; to all onComplete callbacks for memory leak prevention
def inject_cleanup(match):
    return match.group(0).replace(
        "isRecapTransitioning = false;",
        "layer.innerHTML = '';\n                isRecapTransitioning = false;"
    )

js_code = re.sub(
    r"onComplete:\s*\(\)\s*=>\s*\{\s*layer\.style\.display\s*=\s*'none';\s*isRecapTransitioning\s*=\s*false;\s*\}",
    inject_cleanup,
    js_code
)

# 3. Rewrite skiper-30 to a multi-layer parallax effect
old_skiper_30 = """    } else if (type === 'skiper-30') {
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
                layer.innerHTML = '';
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
        });"""

# If the regex already injected layer.innerHTML = '', we should match both possibilities for old_skiper_30 safely
# We will just use regex to replace the entire `else if (type === 'skiper-30') { ... }` block up to `else if (type === 'skiper-71') {`

start_30 = js_code.find("} else if (type === 'skiper-30') {")
end_30 = js_code.find("} else if (type === 'skiper-71') {")

new_skiper_30 = """    } else if (type === 'skiper-30') {
        // Skiper 30 GSAP "Oliver Parallax" Depth Multi-Layer Blur
        layer.style.background = '#000';
        
        // Background layer (slow, highly blurred)
        const bgImg = document.createElement('img');
        bgImg.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        bgImg.style.position = 'absolute';
        bgImg.style.width = '100vw';
        bgImg.style.height = '100vh';
        bgImg.style.objectFit = 'cover';
        bgImg.style.opacity = '0';
        bgImg.style.filter = 'blur(20px)';
        bgImg.style.transform = 'scale(1.2)';
        layer.appendChild(bgImg);
        
        // Midground layer (medium speed, medium blur, smaller)
        const midImg = document.createElement('img');
        midImg.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        midImg.style.position = 'absolute';
        midImg.style.width = '60vw';
        midImg.style.height = '70vh';
        midImg.style.objectFit = 'cover';
        midImg.style.opacity = '0';
        midImg.style.borderRadius = '24px';
        midImg.style.boxShadow = '0 30px 60px rgba(0,0,0,0.8)';
        midImg.style.filter = 'blur(10px)';
        midImg.style.transform = 'scale(0.8) translateY(100px)';
        layer.appendChild(midImg);

        // Foreground layer (fast, sharp, prominent)
        const fgImg = document.createElement('img');
        fgImg.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        fgImg.style.position = 'absolute';
        fgImg.style.width = '40vw';
        fgImg.style.height = '50vh';
        fgImg.style.objectFit = 'cover';
        fgImg.style.opacity = '0';
        fgImg.style.borderRadius = '16px';
        fgImg.style.boxShadow = '0 50px 100px rgba(0,0,0,0.9)';
        fgImg.style.filter = 'blur(0px)';
        fgImg.style.transform = 'scale(0.5) translateY(200px)';
        layer.appendChild(fgImg);
        
        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                layer.innerHTML = '';
                isRecapTransitioning = false;
            }
        });
        
        // Fade in all layers
        tl.to([bgImg, midImg, fgImg], { opacity: 1, duration: 0.4 }, 0);
        
        // Parallax scroll animation
        tl.to(bgImg, { scale: 1.5, filter: 'blur(30px)', duration: 2.0, ease: 'power2.inOut' }, 0);
        tl.to(midImg, { scale: 1.1, translateY: '-150px', filter: 'blur(20px)', duration: 2.0, ease: 'power2.inOut' }, 0);
        tl.to(fgImg, { scale: 1.2, translateY: '-300px', filter: 'blur(10px)', duration: 2.0, ease: 'power2.inOut',
            onUpdate: function() {
                if(this.progress() > 0.6 && callback) {
                    callback();
                    callback = null;
                }
            }
        }, 0);
        
        // Fade out transition layer
        tl.to(layer, { opacity: 0, duration: 0.5, ease: 'power2.in' }, 1.5);
        
"""

js_code = js_code[:start_30] + new_skiper_30 + js_code[end_30:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print("Audited and fixed GSAP transitions, enabled random cycle, built true Oliver Parallax for skiper-30!")
