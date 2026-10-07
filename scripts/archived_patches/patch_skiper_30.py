import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the monolithic if (photos.length >= 3)
old_pattern = r"(if \(photos\.length >= 3\) \{.*?\n    \} else \{)"

new_code = '''const types = photos.length >= 3 ? ['skiper-32', 'skiper-30'] : ['blur'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    if (type === 'skiper-32') {
        // Skiper 32 Scroll Images Reveal
        const grid = document.createElement('div');
        grid.className = 'skiper-32-grid';
        
        const randomValues = [
            {rotateXStart:-45,translateZStart:-450,translateYStart:2150},
            {rotateXStart:-67,translateZStart:-720,translateYStart:1720},
            {rotateXStart:-38,translateZStart:-380,translateYStart:1380},
            {rotateXStart:-82,translateZStart:-890,translateYStart:1890},
            {rotateXStart:-53,translateZStart:-540,translateYStart:2540},
            {rotateXStart:-71,translateZStart:-760,translateYStart:1760},
            {rotateXStart:-42,translateZStart:-420,translateYStart:1420},
            {rotateXStart:-89,translateZStart:-950,translateYStart:1950},
            {rotateXStart:-48,translateZStart:-480,translateYStart:1480},
            {rotateXStart:-75,translateZStart:-800,translateYStart:1800},
            {rotateXStart:-35,translateZStart:-350,translateYStart:1350},
            {rotateXStart:-85,translateZStart:-920,translateYStart:1920},
            {rotateXStart:-58,translateZStart:-580,translateYStart:1580},
            {rotateXStart:-69,translateZStart:-740,translateYStart:1740},
            {rotateXStart:-44,translateZStart:-440,translateYStart:1440},
            {rotateXStart:-78,translateZStart:-830,translateYStart:1830},
            {rotateXStart:-51,translateZStart:-510,translateYStart:1510},
            {rotateXStart:-87,translateZStart:-940,translateYStart:1940},
            {rotateXStart:-39,translateZStart:-390,translateYStart:1390},
            {rotateXStart:-73,translateZStart:-780,translateYStart:1780}
        ];
        
        const items = [];
        for(let i=0; i<20; i++) {
            const img = document.createElement('img');
            img.src = '/api/photo/file/' + encodeURIComponent(photos[i % photos.length]);
            img.className = 'skiper-32-item';
            
            const rv = randomValues[i];
            img.style.transform = `translateY(${rv.translateYStart}px) translateZ(${rv.translateZStart}px) rotateX(${rv.rotateXStart}deg)`;
            img.style.opacity = '0';
            img.style.transition = 'none';
            grid.appendChild(img);
            items.push(img);
        }
        
        layer.appendChild(grid);
        
        // Force reflow
        void grid.offsetWidth;
        
        // Animate In
        items.forEach((img, i) => {
            img.style.transition = 'transform 0.8s cubic-bezier(0.2, 0, 0.2, 1), opacity 0.8s ease';
            img.style.transform = 'translateY(0px) translateZ(0px) rotateX(0deg)';
            img.style.opacity = '1';
        });
        
        setTimeout(() => {
            callback();
            
            // Animate Out (zoom through camera)
            items.forEach((img, i) => {
                const rv = randomValues[i];
                // reverse them but zoom past camera (positive Z)
                img.style.transition = 'transform 0.6s cubic-bezier(0.8, 0, 0.2, 1), opacity 0.5s ease 0.1s';
                img.style.transform = `translateY(${-rv.translateYStart}px) translateZ(200px) rotateX(${-rv.rotateXStart}deg)`;
                img.style.opacity = '0';
            });
            
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 600);
            
        }, 850);
        
    } else if (type === 'skiper-30') {
        // Skiper 30 Parallax Blur Transition
        // Takes a random image, scales it up massively with heavy blur, hiding the slide change inside the blur.
        const img = document.createElement('img');
        img.src = '/api/photo/file/' + encodeURIComponent(photos[Math.floor(Math.random() * photos.length)]);
        img.style.position = 'absolute';
        img.style.width = '100vw';
        img.style.height = '100vh';
        img.style.objectFit = 'cover';
        img.style.opacity = '0';
        img.style.transform = 'scale(1)';
        img.style.filter = 'blur(0px)';
        img.style.transition = 'all 0.6s cubic-bezier(0.8, 0, 0.2, 1)';
        
        layer.appendChild(img);
        
        // Force reflow
        void img.offsetWidth;
        
        // Animate in: rapid zoom and heavy blur
        img.style.opacity = '1';
        img.style.transform = 'scale(1.5)';
        img.style.filter = 'blur(30px)';
        
        setTimeout(() => {
            callback(); // Swap slides while completely blurred
            
            // Animate out: continue zooming, fade out opacity
            img.style.transition = 'all 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)';
            img.style.transform = 'scale(2)';
            img.style.opacity = '0';
            
            setTimeout(() => {
                layer.style.display = 'none';
                isRecapTransitioning = false;
            }, 600);
        }, 600);
        
    } else {'''

js = re.sub(old_pattern, new_code, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Injected Skiper 30 fallback!")
