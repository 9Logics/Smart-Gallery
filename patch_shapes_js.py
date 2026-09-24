import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# We need to completely rewrite the generateYearlyTheme inner logic for the 3 styles.
# Find the start of style logic
start_idx = js.find('const styleType = Math.floor(myRand() * 3);')
end_idx = js.find('}\n}', start_idx) + 1

if start_idx != -1 and end_idx != -1:
    new_style_logic = '''const styleType = Math.floor(myRand() * 3); // 0 = Goopy Circles, 1 = Organic Morphing Blobs, 2 = Large Jagged Shapes
    
    if (styleType === 0) {
        // Goopy Circles (Solid colors melting into each other using a sharp SVG goo filter)
        container.style.filter = "url('#recap-goo')";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<7; i++) {
            const blob = document.createElement('div');
            blob.className = 'theme-blob';
            // Semi-transparent solid colors so they don't overpower images, but no blurred glow
            blob.style.background = palette[i % palette.length];
            blob.style.opacity = "0.85";
            blob.style.left = (myRand() * 80) + 'vw';
            blob.style.top = (myRand() * 80) + 'vh';
            blob.style.animationDuration = (12 + myRand() * 10) + 's';
            blob.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(blob);
        }
    } else if (styleType === 1) {
        // Organic Morphing Blobs (Solid flat colors with animated complex border-radius)
        container.style.filter = "none";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<5; i++) {
            const orb = document.createElement('div');
            orb.className = 'theme-orb';
            orb.style.background = palette[i % palette.length];
            orb.style.opacity = "0.85";
            orb.style.left = (myRand() * 60 - 10) + 'vw';
            orb.style.top = (myRand() * 60 - 10) + 'vh';
            orb.style.animationDuration = (15 + myRand() * 15) + 's';
            orb.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(orb);
        }
    } else {
        // Large Jagged Geometric Shapes
        container.style.filter = "none";
        container.style.mixBlendMode = "normal";
        const polygons = [
            'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)', // Pentagon
            'polygon(25% 0%, 100% 0%, 75% 100%, 0% 100%)', // Parallelogram
            'polygon(50% 0%, 0% 100%, 100% 100%)', // Triangle
            'polygon(40% 0%, 100% 20%, 80% 100%, 0% 80%)', // Irregular quad
            'polygon(0% 15%, 15% 15%, 15% 0%, 85% 0%, 85% 15%, 100% 15%, 100% 85%, 85% 85%, 85% 100%, 15% 100%, 15% 85%, 0% 85%)' // Cross
        ];
        
        for(let i=0; i<12; i++) { // Fewer but much larger shapes
            const shape = document.createElement('div');
            shape.className = 'theme-sharp';
            shape.style.background = palette[i % palette.length];
            shape.style.opacity = "0.85";
            shape.style.left = (myRand() * 80) + 'vw';
            shape.style.top = (myRand() * 80) - 10 + 'vh';
            shape.style.animationDuration = (20 + myRand() * 15) + 's';
            shape.style.animationDelay = '-' + (myRand() * 10) + 's';
            
            shape.style.clipPath = polygons[Math.floor(myRand() * polygons.length)];
            const size = (200 + myRand() * 400) + 'px'; // Huge distinct shapes
            shape.style.width = size;
            shape.style.height = size;
            
            container.appendChild(shape);
        }
    }'''
    
    js = js[:start_idx] + new_style_logic + js[end_idx:]
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated JS theme logic!")
else:
    print("Could not find style logic block.")
