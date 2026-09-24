import os

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

theme_logic = '''
function generateYearlyTheme(year) {
    const container = document.getElementById('theme-canvas');
    if (!container) return;
    container.innerHTML = '';
    
    // Seeded random based on year string
    let seedStr = String(year);
    let seed = 0;
    for (let i = 0; i < seedStr.length; i++) {
        seed += seedStr.charCodeAt(i) * (i + 1);
    }
    
    const myRand = () => {
        let x = Math.sin(seed++) * 10000;
        return x - Math.floor(x);
    };
    
    const palettes = [
        ['#FF0A54', '#FF477E', '#FF7096', '#FF85A1', '#FBB1BD'], // Pink Goo
        ['#00F5D4', '#00BBF9', '#FEE440', '#F15BB5', '#9B5DE5'], // Retro Pop
        ['#FF9A9E', '#FECFEF', '#A1C4FD', '#C2E9FB', '#D4FC79'], // Dreamy Pastel
        ['#FA709A', '#FEE140', '#F3A183', '#556270', '#FF3CAC'], // Sunset Paint
        ['#8EC5FC', '#E0C3FC', '#4FACFE', '#00F2FE', '#38F9D7'], // Frosty Fluid
        ['#ff0055', '#0033ff', '#00ff99', '#ffff00', '#ff00ff']  // Cyber Neon
    ];
    
    const palette = palettes[Math.floor(myRand() * palettes.length)];
    const styleType = Math.floor(myRand() * 3); // 0 = Gooey, 1 = Soft Orbs, 2 = Sharp Confetti
    
    if (styleType === 0) {
        // Gooey Mixing Paint
        container.style.filter = "url('#recap-goo')";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<8; i++) {
            const blob = document.createElement('div');
            blob.className = 'theme-blob';
            blob.style.background = palette[i % palette.length];
            blob.style.left = (myRand() * 80) + 'vw';
            blob.style.top = (myRand() * 80) + 'vh';
            blob.style.animationDuration = (12 + myRand() * 10) + 's';
            blob.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(blob);
        }
    } else if (styleType === 1) {
        // Soft Gradient Orbs
        container.style.filter = "blur(80px)";
        container.style.mixBlendMode = "screen";
        for(let i=0; i<6; i++) {
            const orb = document.createElement('div');
            orb.className = 'theme-orb';
            orb.style.background = palette[i % palette.length];
            orb.style.left = (myRand() * 60 - 10) + 'vw';
            orb.style.top = (myRand() * 60 - 10) + 'vh';
            orb.style.animationDuration = (15 + myRand() * 15) + 's';
            orb.style.animationDelay = '-' + (myRand() * 10) + 's';
            container.appendChild(orb);
        }
    } else {
        // Sharp Geometric Confetti
        container.style.filter = "none";
        container.style.mixBlendMode = "normal";
        for(let i=0; i<40; i++) {
            const shape = document.createElement('div');
            shape.className = 'theme-sharp';
            shape.style.background = palette[i % palette.length];
            shape.style.left = (myRand() * 100) + 'vw';
            shape.style.top = (myRand() * 100) - 20 + 'vh';
            shape.style.animationDuration = (4 + myRand() * 8) + 's';
            shape.style.animationDelay = '-' + (myRand() * 10) + 's';
            
            // Randomly pick triangle, square, or line
            const r = myRand();
            if (r < 0.33) {
                shape.style.clipPath = 'polygon(50% 0%, 0% 100%, 100% 100%)';
                shape.style.width = (30 + myRand() * 60) + 'px';
                shape.style.height = (30 + myRand() * 60) + 'px';
            } else if (r < 0.66) {
                shape.style.borderRadius = (myRand() * 20) + 'px'; // rounded rect
                shape.style.width = (20 + myRand() * 50) + 'px';
                shape.style.height = (20 + myRand() * 50) + 'px';
            } else {
                shape.style.borderRadius = '50%';
                shape.style.width = (10 + myRand() * 40) + 'px';
                shape.style.height = shape.style.width;
            }
            
            container.appendChild(shape);
        }
    }
}
'''

call_logic = '''
            // Set backdrop (Parallax)
            const backdropImg = data.memorable_moment || (clone.querySelector('img') ? clone.querySelector('img').src : '');
            if (backdropImg) {
                document.getElementById('recap-backdrop').style.backgroundImage = `url('/api/photo/file/${encodeURIComponent(backdropImg)}')`;
                document.getElementById('recap-stat-place-img').src = `/api/photo/thumbnail/${encodeURIComponent(backdropImg)}`;
            }
            
            // Generate dynamic yearly background theme
            generateYearlyTheme(fetchYear);
'''

if 'generateYearlyTheme' not in js:
    js += '\n' + theme_logic
    # Replace the backdrop logic to also call generateYearlyTheme
    js = js.replace('''
            // Set backdrop (Parallax)
            const backdropImg = data.memorable_moment || (clone.querySelector('img') ? clone.querySelector('img').src : '');
            if (backdropImg) {
                document.getElementById('recap-backdrop').style.backgroundImage = `url('/api/photo/file/${encodeURIComponent(backdropImg)}')`;
                document.getElementById('recap-stat-place-img').src = `/api/photo/thumbnail/${encodeURIComponent(backdropImg)}`;
            }
''', call_logic)
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Injected JS theme generation logic!")
else:
    print("Theme JS already exists.")
