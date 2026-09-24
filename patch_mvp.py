import os

# 1. Update style.css
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

recap_css = '''
/* --- STORY MODE / RECAP MVP --- */
.recap-trigger {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    opacity: 0.8;
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.recap-trigger:hover {
    opacity: 1;
    transform: translateX(-50%) translateY(-5px);
}

.recap-glow {
    position: absolute;
    bottom: -20px;
    width: 150px;
    height: 50px;
    background: radial-gradient(ellipse at bottom, rgba(150, 50, 255, 0.6) 0%, transparent 70%);
    filter: blur(10px);
    pointer-events: none;
    animation: recapBreathe 3s ease-in-out infinite alternate;
}

@keyframes recapBreathe {
    0% { opacity: 0.5; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1.1); }
}

.recap-trigger svg {
    color: white;
    width: 24px;
    height: 24px;
    drop-shadow: 0 2px 5px rgba(0,0,0,0.5);
    z-index: 2;
    animation: recapBounce 2s infinite;
}

@keyframes recapBounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

/* The Wipe Effect */
body {
    transition: background-color 0.8s ease;
}

body.recap-active {
    background-color: #050505;
    overflow: hidden;
}

body.recap-active .main-content, 
body.recap-active .sidebar,
body.recap-active .header-area {
    transform: scale(0.9) translateY(-40px);
    filter: blur(15px);
    opacity: 0;
    pointer-events: none;
}

.main-content, .sidebar, .header-area {
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), filter 0.8s ease, opacity 0.6s ease;
}

/* Recap Container */
.recap-container {
    position: fixed;
    top: 100vh; /* Start below screen */
    left: 0;
    width: 100vw;
    height: 100vh;
    background: #050505;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    color: white;
    overflow: hidden;
}

body.recap-active .recap-container {
    transform: translateY(-100vh);
}

.recap-title {
    font-size: 3rem;
    font-weight: 800;
    font-family: system-ui, -apple-system, sans-serif;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #ff00cc, #3333ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 1s ease 0.8s, transform 1s ease 0.8s;
}

body.recap-active .recap-title {
    opacity: 1;
    transform: translateY(0);
}

.recap-close {
    position: absolute;
    top: 20px;
    right: 20px;
    cursor: pointer;
    opacity: 0.5;
    transition: opacity 0.3s;
}

.recap-close:hover {
    opacity: 1;
}
'''
if 'STORY MODE / RECAP MVP' not in css_content:
    css_content += recap_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)

# 2. Update index.html
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

recap_html = '''
    <!-- STORY MODE / RECAP TRIGGER -->
    <div class="recap-trigger" id="recap-trigger" onclick="toggleRecap()">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
        <div class="recap-glow"></div>
    </div>

    <!-- STORY MODE / RECAP CONTAINER -->
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
    </script>
</body>'''

if 'id="recap-trigger"' not in html_content:
    html_content = html_content.replace('</body>', recap_html)
    html_content = html_content.replace('v=241', 'v=242')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

print("MVP implemented")
