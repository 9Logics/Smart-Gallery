import re

html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

# Replace the HTML block
html_code = re.sub(
    r"<!-- Skiper11: Pixel Preloader -->.*?</div>.*?</div>.*?</div>\s*</div>",
    """<!-- Sleek Dashboard Preloader -->
        <div class="sleek-preloader" id="pixel-preloader">
            <div class="sleek-backdrop-blur"></div>
            <div class="sleek-word-wrapper">
                <div class="sleek-word" id="pixel-counter">CURATING</div>
            </div>
            <div class="sleek-progress-bar">
                <div class="sleek-progress-fill" id="pixel-grid"></div>
            </div>
        </div>""",
    html_code,
    flags=re.DOTALL
)

# Replace the JS setup
html_code = re.sub(
    r"// Set up Skiper11 Pixel Grid Preloader.*?grid\.innerHTML = '';",
    """// Set up Sleek Dashboard Preloader
                const preloader = document.getElementById('pixel-preloader');
                const wordEl = document.getElementById('pixel-counter');
                const progressEl = document.getElementById('pixel-grid');
                
                preloader.style.display = 'flex';
                preloader.style.opacity = '1';
                progressEl.style.width = '0%';""",
    html_code,
    flags=re.DOTALL
)

# Replace the Simulate Loading JS logic
html_code = re.sub(
    r"// Simulate Loading for Pixel Preloader.*?}, 100\);",
    """// Simulate Loading
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
                }, 100);""",
    html_code,
    flags=re.DOTALL
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print("index.html patched heavily!")
