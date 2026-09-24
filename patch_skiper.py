import os
import re

# --- HTML Update ---
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

old_html = '''<!-- STORY MODE / RECAP CONTAINER -->
    <div class="recap-container" id="recap-container">
        <div class="recap-close" onclick="toggleRecap()">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </div>
        <h1 class="recap-title">Your 2026 Rewind</h1>
    </div>

    <script>
        function toggleRecap() {
            document.body.classList.toggle('recap-active');
        }
    </script>'''

new_html = '''<!-- STORY MODE / RECAP CONTAINER -->
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

if old_html in html_content:
    html_content = html_content.replace(old_html, new_html)
    html_content = html_content.replace('v=244', 'v=245')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("HTML updated")
else:
    print("HTML not found!")


# --- CSS Update ---
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

old_css = '''.recap-title {
    font-size: 5rem;
    font-weight: 400;
    font-family: 'Abril Fatface', serif;
    background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 4px 15px rgba(255, 255, 255, 0.2));
    margin: 0;
    /* Use extreme negative inset for top, bottom, and left to completely prevent clipping! */
    clip-path: inset(-50% 100% -50% -50%);
    opacity: 0;
    transform: scale(0.95);
    letter-spacing: 0.02em;
}

body.recap-active .recap-title {
    opacity: 1;
    /* Combine the left-to-right wipe with a very subtle scale up for extra premium feel */
    animation: 
        fancyReveal 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.8s forwards,
        fancyScale 3s ease-out 0.8s forwards;
}

@keyframes fancyReveal {
    0% { clip-path: inset(-50% 100% -50% -50%); }
    100% { clip-path: inset(-50% -10% -50% -50%); }
}

@keyframes fancyScale {
    0% { transform: scale(0.95); }
    100% { transform: scale(1); }
}'''

new_css = '''/* Preloader CSS */
.recap-preloader {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #050505;
    z-index: 10;
    transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), filter 0.6s ease;
}

.recap-preloader.finished {
    opacity: 0;
    pointer-events: none;
    transform: scale(1.1);
    filter: blur(10px);
}

.recap-preloader-text {
    font-family: var(--font-mono, monospace);
    font-size: 12px;
    letter-spacing: 4px;
    color: rgba(255,255,255,0.7);
    margin-bottom: 24px;
}

.recap-preloader-bar {
    width: 250px;
    height: 1px;
    background: rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}

.recap-preloader-progress {
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 0%;
    background: #fff;
    box-shadow: 0 0 10px rgba(255,255,255,0.8);
    transition: width 0.1s ease-out;
}

/* Skiper Text Reveal Animation */
.recap-title {
    font-size: 5rem;
    font-weight: 400;
    font-family: 'Abril Fatface', serif;
    background: linear-gradient(135deg, #ffffff 0%, #aaaaaa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 4px 20px rgba(255, 255, 255, 0.15));
    margin: 0;
    display: flex;
    letter-spacing: 0.02em;
}

.recap-title span {
    display: inline-block;
    transform: translateY(60px) scale(0.8) rotate(15deg);
    opacity: 0;
    filter: blur(12px);
    will-change: transform, opacity, filter;
}

.recap-title.revealed span {
    animation: skiperTextReveal 0.9s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes skiperTextReveal {
    0% { transform: translateY(60px) scale(0.8) rotate(15deg); opacity: 0; filter: blur(12px); }
    100% { transform: translateY(0) scale(1) rotate(0deg); opacity: 1; filter: blur(0px); }
}'''

if old_css in css_content:
    css_content = css_content.replace(old_css, new_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("CSS updated")
else:
    print("CSS not found!")
