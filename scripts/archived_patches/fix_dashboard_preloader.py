import re

# 1. Update index.html HTML structure
html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

old_html = """        <!-- Skiper11: Pixel Preloader -->
        <div class="pixel-preloader" id="pixel-preloader">
            <div class="window-ai-gradient"></div>
            <div class="pixel-counter" id="pixel-counter">0%</div>
            <div class="pixel-grid" id="pixel-grid"></div>
        </div>"""

new_html = """        <!-- Sleek Dashboard Preloader -->
        <div class="sleek-preloader" id="pixel-preloader">
            <div class="sleek-backdrop-blur"></div>
            <div class="sleek-word-wrapper">
                <div class="sleek-word" id="pixel-counter">CURATING</div>
            </div>
            <div class="sleek-progress-bar">
                <div class="sleek-progress-fill" id="pixel-grid"></div>
            </div>
        </div>"""

if old_html in html_code:
    html_code = html_code.replace(old_html, new_html)
else:
    print("Warning: Could not find old HTML.")

# 2. Update index.html inline JS
old_js = """                // Set up Skiper11 Pixel Grid Preloader
                const preloader = document.getElementById('pixel-preloader');
                const counter = document.getElementById('pixel-counter');
                const grid = document.getElementById('pixel-grid');
                preloader.style.display = 'flex';
                counter.style.opacity = '1';
                grid.innerHTML = '';
                
                // Set up Hero Title Animation
                const title = document.querySelector('.recap-hero h1');
                title.classList.remove('revealed');
                title.innerHTML = '';
                
                // Break title into words for line-up animation
                const words = ["YOUR", "YEAR", "IN", "REVIEW"];
                words.forEach((word, idx) => {
                    const wrapper = document.createElement('span');
                    wrapper.className = 'word-wrapper';
                    const inner = document.createElement('span');
                    inner.className = 'word-inner';
                    inner.style.transitionDelay = `${idx * 0.1}s`;
                    inner.innerText = word;
                    
                    wrapper.appendChild(inner);
                    title.appendChild(wrapper);
                });

                // Simulate Loading for Pixel Preloader
                let count = 0;
                const interval = setInterval(() => {
                    count += Math.floor(Math.random() * 10) + 5;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        
                        // Pixel Wipe Animation (slef.me style)
                        counter.style.opacity = '0';
                        const blocks = Array.from(grid.children);
                        // Shuffle array for random pixel disappearance
                        blocks.sort(() => Math.random() - 0.5);
                        
                        // Start text reveal underneath the pixels!
                        title.classList.add('revealed');

                        const totalDuration = 800; // Wipe finishes in 0.8s total
                        const staggerDelay = totalDuration / blocks.length;

                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * staggerDelay);
                        });
                        
                        setTimeout(() => {
                            preloader.style.opacity = '0'; // Smooth fade out
                            setTimeout(() => {
                                preloader.style.display = 'none';
                            }, 800);
                            
                            // 1.5 seconds after reveal, morph to options
                            setTimeout(() => {
                                document.getElementById('recap-container').classList.add('options-active');
                                document.getElementById('rewind-dashboard').classList.add('active');
                            }, 1500);
                        }, totalDuration + 200);
                    } else {
                        counter.innerText = count + '%';
                        
                        // Add some random pixels
                        for(let i=0; i<3; i++) {
                            const p = document.createElement('div');
                            p.className = 'pixel';
                            p.style.left = Math.random() * 100 + '%';
                            p.style.top = Math.random() * 100 + '%';
                            grid.appendChild(p);
                        }
                    }
                }, 100);"""

new_js = """                // Set up Sleek Dashboard Preloader
                const preloader = document.getElementById('pixel-preloader');
                const wordEl = document.getElementById('pixel-counter');
                const progressEl = document.getElementById('pixel-grid');
                
                preloader.style.display = 'flex';
                preloader.style.opacity = '1';
                progressEl.style.width = '0%';
                
                // Set up Hero Title Animation
                const title = document.querySelector('.recap-hero h1');
                title.classList.remove('revealed');
                title.innerHTML = '';
                
                // Break title into words for line-up animation
                const headlineWords = ["YOUR", "YEAR", "IN", "REVIEW"];
                headlineWords.forEach((word, idx) => {
                    const wrapper = document.createElement('span');
                    wrapper.className = 'word-wrapper';
                    const inner = document.createElement('span');
                    inner.className = 'word-inner';
                    inner.style.transitionDelay = `${idx * 0.1}s`;
                    inner.innerText = word;
                    wrapper.appendChild(inner);
                    title.appendChild(wrapper);
                });

                // Simulate Loading
                const loadingWords = ["GATHERING", "ANALYZING", "CURATING", "MAPPING", "READY."];
                let wIndex = 0;
                let count = 0;
                wordEl.innerText = loadingWords[0];
                
                // GSAP word change animation
                if (window.gsap) gsap.fromTo(wordEl, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power3.out" });

                const wordInterval = setInterval(() => {
                    wIndex++;
                    if (wIndex >= loadingWords.length - 1) {
                        clearInterval(wordInterval);
                    } else {
                        if (window.gsap) {
                            gsap.fromTo(wordEl, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power3.out" });
                        }
                        wordEl.innerText = loadingWords[wIndex];
                    }
                }, 400);

                const interval = setInterval(() => {
                    count += Math.random() * 12 + 5;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        clearInterval(wordInterval);
                        
                        wordEl.innerText = loadingWords[loadingWords.length - 1]; // "READY."
                        progressEl.style.width = '100%';
                        
                        title.classList.add('revealed');
                        
                        setTimeout(() => {
                            if (window.gsap) {
                                gsap.to(preloader, { opacity: 0, duration: 0.8, onComplete: () => {
                                    preloader.style.display = 'none';
                                }});
                            } else {
                                preloader.style.opacity = '0';
                                setTimeout(() => preloader.style.display = 'none', 800);
                            }
                            
                            setTimeout(() => {
                                document.getElementById('recap-container').classList.add('options-active');
                                document.getElementById('rewind-dashboard').classList.add('active');
                            }, 500);
                        }, 400);
                    } else {
                        progressEl.style.width = count + '%';
                    }
                }, 100);"""

if old_js in html_code:
    html_code = html_code.replace(old_js, new_js)
else:
    print("Warning: Could not find old JS.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

# 3. Update style.css
css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

old_css = """/* Skiper11: Pixel Preloader */
.pixel-preloader {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    transition: opacity 0.8s ease;
}

.pixel-counter {
    position: absolute;
    font-family: var(--font-mono, monospace);
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    z-index: 2;
    transition: opacity 0.3s;
}

.pixel-grid {
    position: absolute;
    inset: 0;
    z-index: 1;
}

.pixel {
    position: absolute;
    width: 20px;
    height: 20px;
    background: #fff;
    opacity: 0.1;
    transition: opacity 0.3s;
}"""

new_css = """/* Sleek Dashboard Preloader */
.sleek-preloader {
    position: absolute;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 50;
    flex-direction: column;
    transition: opacity 0.8s ease;
}
.sleek-backdrop-blur {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
}
.sleek-word-wrapper {
    position: relative;
    z-index: 2;
    overflow: hidden;
    height: 80px;
}
.sleek-word {
    font-size: clamp(30px, 6vw, 60px);
    font-weight: 800;
    letter-spacing: -2px;
    color: #fff;
    text-transform: uppercase;
    line-height: 80px;
    font-family: 'Outfit', sans-serif;
}
.sleek-progress-bar {
    position: relative;
    z-index: 2;
    width: 250px;
    height: 3px;
    background: rgba(255,255,255,0.1);
    margin-top: 10px;
    border-radius: 3px;
    overflow: hidden;
}
.sleek-progress-fill {
    width: 0%;
    height: 100%;
    background: #fff;
    transition: width 0.1s linear;
}"""

if old_css in css_code:
    css_code = css_code.replace(old_css, new_css)
else:
    print("Warning: Could not find old CSS. Attempting regex replacement.")
    css_code = re.sub(r"/\* Skiper11: Pixel Preloader \*/.*?\.pixel \{.*?\transition: opacity 0\.3s;\n\}", new_css, css_code, flags=re.DOTALL)
    if "Sleek Dashboard Preloader" not in css_code:
        css_code += "\n\n" + new_css

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_code)

print("Dashboard sleek preloader patch complete.")
