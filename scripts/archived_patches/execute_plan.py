import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# 1. Update Autoplay for Skiper 47
if "autoplay:" not in js_code:
    js_code = re.sub(
        r"(new Swiper\('\.skiper-47-swiper', \{.*?)loop:\s*true,", 
        r"\1loop: true,\n        speed: 800,\n        autoplay: { delay: 2500, disableOnInteraction: false },", 
        js_code, flags=re.DOTALL
    )

# 2. Update Autoplay for Skiper 54
js_code = re.sub(
    r"(new Swiper\('\.skiper-54-swiper', \{.*?)loop:\s*true,", 
    r"\1loop: true,\n        speed: 800,\n        autoplay: { delay: 2500, disableOnInteraction: false },", 
    js_code, flags=re.DOTALL
)

# 3. Add new transitions to the types array
js_code = js_code.replace(
    "const types = photos.length > 0 ? ['skiper-32', 'skiper-30', 'skiper-71', 'skiper-33'] : ['blur'];",
    "const types = photos.length > 0 ? ['skiper-32', 'skiper-30', 'skiper-71', 'skiper-33', 'skiper-41', 'skiper-48', 'skiper-34'] : ['blur'];"
)

# 4. Inject new transition implementations before `} else if (type === 'blur') {`
new_transitions = """    } else if (type === 'skiper-41') {
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.opacity = '0';
        img.style.transform = 'scale(1)';
        img.style.filter = 'brightness(1) blur(0px)';
        layer.appendChild(img);

        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                layer.innerHTML = '';
                isRecapTransitioning = false;
            }
        });

        tl.to(img, { opacity: 1, duration: 0.2 });
        tl.to(img, {
            scale: 1.5,
            filter: 'brightness(3) blur(20px)',
            opacity: 0,
            duration: 1.0,
            ease: "power2.in",
            onUpdate: function() {
                if(this.progress() > 0.7 && callback) {
                    callback();
                    callback = null;
                }
            }
        });
    } else if (type === 'skiper-48') {
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '60vw';
        img.style.height = '70vh';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '24px';
        img.style.boxShadow = '0 20px 50px rgba(0,0,0,0.6)';
        img.style.top = '15vh';
        img.style.left = '20vw';
        img.style.transformOrigin = 'bottom left';
        layer.appendChild(img);

        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                layer.innerHTML = '';
                isRecapTransitioning = false;
            }
        });

        tl.fromTo(img, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.5)" });
        tl.to(img, {
            x: '100vw',
            y: '-20vh',
            rotationZ: 45,
            duration: 0.6,
            ease: "power3.in",
            onUpdate: function() {
                if(this.progress() > 0.4 && callback) {
                    callback();
                    callback = null;
                }
            }
        }, "+=0.2");
    } else if (type === 'skiper-34') {
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '200vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.left = '0';
        layer.appendChild(img);

        let tl = gsap.timeline({
            onComplete: () => {
                layer.style.display = 'none';
                layer.innerHTML = '';
                isRecapTransitioning = false;
            }
        });

        tl.to(img, {
            x: '-100vw',
            filter: 'blur(30px)',
            duration: 0.7,
            ease: "power2.inOut",
            onUpdate: function() {
                if(this.progress() > 0.5 && callback) {
                    callback();
                    callback = null;
                }
            }
        });
"""

js_code = js_code.replace("} else if (type === 'blur') {", new_transitions + "    } else if (type === 'blur') {")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Updated JS with Autoplay and 3 new transitions!")
