import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Skiper 37 Number Flow Animation JS
num_flow_js = '''
// Skiper37 Number Flow Animation
function animateNumberFlow(obj, start, end, duration) {
    obj.innerHTML = '';
    const endStr = String(end);
    
    for (let i = 0; i < endStr.length; i++) {
        const targetDigit = parseInt(endStr[i]);
        const column = document.createElement('div');
        column.className = 'number-flow-digit';
        
        // We will create a strip of numbers 0-9 repeatedly, then stop at the target
        let strip = '';
        // Add 20 digits to scroll through for effect
        for(let j=0; j<20; j++) {
            strip += `<span>${j % 10}</span>`;
        }
        strip += `<span>${targetDigit}</span>`;
        column.innerHTML = strip;
        obj.appendChild(column);
        
        // Trigger animation
        requestAnimationFrame(() => {
            const digitHeight = 100; // matches line-height
            const totalScroll = 20 * digitHeight;
            column.style.transform = `translateY(-${totalScroll}px)`;
            // Stagger columns slightly
            column.style.transitionDelay = `${i * 0.1}s`;
        });
    }
}
'''

# 2. Skiper 29 Siena Depth Hover
siena_js = '''
// Skiper29 Siena Parallax Depth Hover
document.addEventListener('mousemove', (e) => {
    const slides = document.querySelectorAll('.recap-slide.active');
    if(slides.length === 0) return;
    
    const slide = slides[0];
    const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
    
    // Tilt the slide container
    slide.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    
    // Move individual layers based on depth
    const layers = slide.querySelectorAll('.siena-layer');
    layers.forEach(layer => {
        const depth = layer.getAttribute('data-depth') || 20;
        const xOffset = (window.innerWidth / 2 - e.pageX) * (depth / 1000);
        const yOffset = (window.innerHeight / 2 - e.pageY) * (depth / 1000);
        layer.style.transform = `translateZ(${depth}px) translate(${xOffset}px, ${yOffset}px)`;
    });
});
'''

if 'animateNumberFlow' not in js:
    js = js.replace('function animateValue', num_flow_js + '\n' + siena_js + '\nfunction animateValue')
    
    # Replace animateValue calls in showRecapSlide
    js = js.replace('animateValue(p, 0, recapData.total_photos, 2000);', 'animateNumberFlow(p, 0, recapData.total_photos, 2000);')
    js = js.replace('animateValue(v, 0, recapData.total_videos, 2000);', 'animateNumberFlow(v, 0, recapData.total_videos, 2000);')
    
    # Skiper30 populating gallery
    gallery_logic = '''
            // Skiper 30 Parallax Gallery
            const gallery = document.getElementById('recap-parallax-gallery');
            gallery.innerHTML = '';
            if (data.gallery_photos && data.gallery_photos.length > 0) {
                data.gallery_photos.forEach((photoPath, i) => {
                    if(i > 4) return; // Limit to 5 background photos
                    const img = document.createElement('img');
                    img.src = `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
                    img.className = `parallax-gallery-item p-item-${i+1}`;
                    gallery.appendChild(img);
                });
            }
'''
    js = js.replace('// Set backdrop (Parallax)', gallery_logic + '\n            // Set backdrop (Parallax)')
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Injected Skiper JS features!")
else:
    print("Skiper JS already exists!")
