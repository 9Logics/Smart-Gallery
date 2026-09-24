import os

# --- HTML Update ---
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# I will replace the old recap-container with the new one
old_recap = '''<!-- STORY MODE / RECAP CONTAINER -->
    <div class="recap-container" id="recap-container">
        <div class="recap-close" onclick="toggleRecap()">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </div>
        
        <!-- Preloader -->
        <div class="recap-preloader" id="recap-preloader">
            <div class="recap-preloader-text" id="recap-preloader-text">0%</div>
            <div class="recap-preloader-bar"><div class="recap-preloader-progress" id="recap-preloader-progress"></div></div>
        </div>

        <h1 class="recap-title" id="recap-title">Your 2026 Rewind</h1>
    </div>

    <script>
        function toggleRecap() {
            const body = document.body;
            body.classList.toggle('recap-active');
            
            if (body.classList.contains('recap-active')) {
                // Initialize Preloader
                let count = 0;
                const counterEl = document.getElementById('recap-preloader-text');
                const progressEl = document.getElementById('recap-preloader-progress');
                const preloader = document.getElementById('recap-preloader');
                preloader.classList.remove('finished');
                
                // Initialize Skiper-style Split Text
                const title = document.getElementById('recap-title');
                title.innerHTML = '';
                title.classList.remove('revealed');
                
                const text = "Your 2026 Rewind";
                text.split('').forEach((char, i) => {
                    const span = document.createElement('span');
                    span.innerText = char === ' ' ? '\\u00A0' : char;
                    span.style.animationDelay = (i * 0.04) + 's';
                    title.appendChild(span);
                });

                // Simulate Loading
                const interval = setInterval(() => {
                    count += Math.floor(Math.random() * 15) + 5;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        
                        // Finish preloader and trigger text reveal
                        setTimeout(() => {
                            preloader.classList.add('finished');
                            setTimeout(() => {
                                title.classList.add('revealed');
                            }, 400); // Wait for preloader to fade
                        }, 300);
                    }
                    counterEl.innerText = count + '%';
                    progressEl.style.width = count + '%';
                }, 40);
            }
        }
    </script>'''

new_recap = '''<!-- STORY MODE / RECAP CONTAINER -->
    <div class="recap-container" id="recap-container">
        <div class="recap-close" onclick="toggleRecap()">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </div>
        
        <!-- Skiper11: Pixel Preloader -->
        <div class="pixel-preloader" id="pixel-preloader">
            <div class="pixel-counter" id="pixel-counter">0%</div>
            <div class="pixel-grid" id="pixel-grid"></div>
        </div>

        <!-- Skiper27: Rolling Text -->
        <h1 class="rolling-text-title" id="recap-title"></h1>
    </div>

    <script>
        function toggleRecap() {
            const body = document.body;
            body.classList.toggle('recap-active');
            
            if (body.classList.contains('recap-active')) {
                // Set up Skiper11 Pixel Grid Preloader
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
                }

                // Set up Skiper27 Rolling Text
                const title = document.getElementById('recap-title');
                title.innerHTML = '';
                title.classList.remove('revealed');
                
                const text = "Your 2026 Rewind";
                text.split('').forEach((char, i) => {
                    const wrapper = document.createElement('span');
                    wrapper.className = 'roll-char-wrap';
                    
                    const inner = document.createElement('span');
                    inner.className = 'roll-char';
                    inner.innerText = char === ' ' ? '\\u00A0' : char;
                    // Custom speed: 0.05 delay between letters
                    inner.style.transitionDelay = (i * 0.05) + 's';
                    
                    wrapper.appendChild(inner);
                    title.appendChild(wrapper);
                });

                // Simulate Loading for Pixel Preloader
                let count = 0;
                const interval = setInterval(() => {
                    count += Math.floor(Math.random() * 20) + 10;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        
                        // Pixel Wipe Animation (slef.me style)
                        counter.style.opacity = '0';
                        const blocks = Array.from(grid.children);
                        // Shuffle array for random pixel disappearance
                        blocks.sort(() => Math.random() - 0.5);
                        
                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * 8); // extremely fast granular reveal
                        });
                        
                        // Wait for grid to finish wiping, then reveal text
                        setTimeout(() => {
                            preloader.style.display = 'none';
                            title.classList.add('revealed');
                        }, blocks.length * 8 + 100);
                    }
                    counter.innerText = count + '%';
                }, 80);
            }
        }
    </script>'''

if old_recap in html_content:
    html_content = html_content.replace(old_recap, new_recap)
    html_content = html_content.replace('v=245', 'v=246')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("HTML updated with Skiper UI 11 & 27")
else:
    print("HTML block not found!")


# --- CSS Update ---
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

# I will replace the previous preloader and recap-title CSS
old_css_start = "/* Preloader CSS */"
new_css = '''/* Skiper11: Pixel Preloader */
.pixel-preloader {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}

.pixel-counter {
    position: absolute;
    font-family: var(--font-mono, monospace);
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    z-index: 12;
    transition: opacity 0.2s ease;
}

.pixel-grid {
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
}

/* Skiper27: Rolling Text */
.rolling-text-title {
    font-size: 5rem;
    font-weight: 400;
    font-family: 'Abril Fatface', serif; /* Or var(--font-display) */
    background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 4px 15px rgba(255, 255, 255, 0.2));
    margin: 0;
    display: flex;
}

.roll-char-wrap {
    display: inline-block;
    overflow: hidden;
    vertical-align: top;
    /* Extra padding to prevent clipping of the serif tail */
    padding-bottom: 20px;
    margin-bottom: -20px;
}

.roll-char {
    display: inline-block;
    transform: translateY(100%);
    /* smooth rolling character transition */
    transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
    will-change: transform;
}

.rolling-text-title.revealed .roll-char {
    transform: translateY(0);
}'''

# Replace from old_css_start to the end of the file since it was added at the bottom
start_index = css_content.find(old_css_start)
if start_index != -1:
    css_content = css_content[:start_index] + new_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("CSS updated with Skiper UI 11 & 27")
else:
    print("CSS block not found!")
