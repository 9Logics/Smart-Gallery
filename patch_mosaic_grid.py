import os

# --- Update HTML JS Logic ---
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''                // Set up Skiper11 Pixel Grid Preloader
                const preloader = document.getElementById('pixel-preloader');
                const counter = document.getElementById('pixel-counter');
                const grid = document.getElementById('pixel-grid');
                preloader.style.display = 'flex';
                counter.style.opacity = '1';
                grid.innerHTML = '';
                
                // Create a 10x10 grid for the pixel wipe
                const totalBlocks = 100;
                for (let i = 0; i < totalBlocks; i++) {
                    const block = document.createElement('div');
                    block.className = 'pixel-block';
                    grid.appendChild(block);
                }'''

new_js = '''                // Set up Skiper11 Pixel Grid Preloader
                const preloader = document.getElementById('pixel-preloader');
                const counter = document.getElementById('pixel-counter');
                const grid = document.getElementById('pixel-grid');
                preloader.style.display = 'flex';
                counter.style.opacity = '1';
                grid.innerHTML = '';
                
                // Grab images from the page to use as mosaic thumbnails
                const availableImages = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                
                // Calculate perfect responsive grid to cover the screen
                const blockSize = 80;
                const cols = Math.ceil(window.innerWidth / blockSize);
                const rows = Math.ceil(window.innerHeight / blockSize);
                const totalBlocks = cols * rows;
                
                grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
                grid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
                
                for (let i = 0; i < totalBlocks; i++) {
                    const block = document.createElement('div');
                    block.className = 'pixel-block';
                    
                    // 40% chance to put a thumbnail in the block
                    if (Math.random() < 0.4 && availableImages.length > 0) {
                        const randomImg = availableImages[Math.floor(Math.random() * availableImages.length)];
                        block.style.backgroundImage = `url(${randomImg})`;
                    }
                    
                    grid.appendChild(block);
                }'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=249', 'v=250')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS grid generation!")
else:
    print("Could not find JS block!")


# --- Update CSS Grid ---
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_css = '''.pixel-grid {
    position: absolute;
    inset: 0;
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    grid-template-rows: repeat(10, 1fr);
    z-index: 11;
}

.pixel-block {
    background-color: #050505;
    width: 100%;
    height: 100%;
    /* Hard pixel cuts, no smooth transitions so it looks retro */
    transition: opacity 0s;
}'''

new_css = '''.pixel-grid {
    position: absolute;
    inset: 0;
    display: grid;
    z-index: 11;
    overflow: hidden;
}

.pixel-block {
    background-color: #050505;
    /* Skiper11 visible grid borders */
    border: 1px solid rgba(255, 255, 255, 0.08);
    width: 100%;
    height: 100%;
    /* Image thumbnail styles */
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    transition: opacity 0s;
    /* slight dimming so text is still readable if a block doesn't shatter immediately */
    box-shadow: inset 0 0 0 1000px rgba(0,0,0,0.4); 
}'''

if old_css in css:
    css = css.replace(old_css, new_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed CSS grid styles!")
else:
    print("Could not find CSS block!")
