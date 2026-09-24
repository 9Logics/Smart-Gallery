import os

# --- HTML JS Logic Update ---
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add the Rewind Options HTML right after the title
old_html = '<h1 class="rolling-text-title" id="recap-title"></h1>'
new_html = '''<h1 class="rolling-text-title" id="recap-title"></h1>
        
        <!-- Rewind Options Cards -->
        <div class="rewind-options" id="rewind-options">
            <div class="rewind-card">
                <div class="rewind-icon"><i data-lucide="sparkles"></i></div>
                <h3>2026 Recap</h3>
                <p>Your entire year in review</p>
                <button class="btn btn-primary rewind-play-btn">Play Recap</button>
            </div>
            
            <div class="rewind-card">
                <div class="rewind-icon"><i data-lucide="calendar"></i></div>
                <h3>Monthly Rewind</h3>
                <p>Look back at a specific month</p>
                <select class="rewind-select">
                    <option value="" disabled selected>Select Month</option>
                    <option>August 2026</option>
                    <option>July 2026</option>
                    <option>June 2026</option>
                    <option>May 2026</option>
                    <option>April 2026</option>
                </select>
                <button class="btn btn-secondary rewind-play-btn">Play Month</button>
            </div>
            
            <div class="rewind-card">
                <div class="rewind-icon"><i data-lucide="history"></i></div>
                <h3>Past Recaps</h3>
                <p>Rediscover previous years</p>
                <select class="rewind-select">
                    <option value="" disabled selected>Select Year</option>
                    <option>2025</option>
                    <option>2024</option>
                    <option>2023</option>
                </select>
                <button class="btn btn-secondary rewind-play-btn">Play Year</button>
            </div>
        </div>'''

if old_html in html:
    html = html.replace(old_html, new_html)

# Add the morph trigger in JS
old_js = '''                        setTimeout(() => {
                            preloader.style.display = 'none';
                        }, totalDuration + 100);'''
new_js = '''                        setTimeout(() => {
                            preloader.style.display = 'none';
                            
                            // 1.5 seconds after reveal, morph to options
                            setTimeout(() => {
                                document.getElementById('recap-container').classList.add('options-active');
                                // Re-initialize lucide icons for the new cards
                                if (window.lucide) {
                                    window.lucide.createIcons();
                                }
                            }, 1500);
                        }, totalDuration + 100);'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=255', 'v=256')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML updated with rewind options!")
else:
    print("Could not find HTML block!")


# --- CSS Update ---
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Add transition to title and options CSS
old_title_css = '''.rolling-text-title {
    font-size: 6rem;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    text-transform: uppercase;
    letter-spacing: -0.04em;
    filter: drop-shadow(0px 8px 24px rgba(255, 255, 255, 0.2));
    margin: 0;
    display: flex;
}'''

new_title_css = '''.rolling-text-title {
    font-size: 6rem;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    text-transform: uppercase;
    letter-spacing: -0.04em;
    filter: drop-shadow(0px 8px 24px rgba(255, 255, 255, 0.2));
    margin: 0;
    display: flex;
    transition: transform 1s cubic-bezier(0.16, 1, 0.3, 1), filter 1s ease;
    transform-origin: center center;
    z-index: 20;
}
.recap-container.options-active .rolling-text-title {
    transform: translateY(-35vh) scale(0.35);
    filter: drop-shadow(0px 4px 12px rgba(255, 255, 255, 0.4));
}

/* Rewind Options UI */
.rewind-options {
    position: absolute;
    top: 55%; /* Slightly below center */
    left: 50%;
    transform: translate(-50%, -20%);
    opacity: 0;
    pointer-events: none;
    display: flex;
    gap: 24px;
    z-index: 19;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transition-delay: 0.3s; /* waits for title morph */
}
.recap-container.options-active .rewind-options {
    opacity: 1;
    pointer-events: all;
    transform: translate(-50%, -50%);
}

.rewind-card {
    background: rgba(25, 25, 35, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 28px;
    padding: 32px 24px;
    width: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    backdrop-filter: blur(24px) saturate(150%);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
}
.rewind-card:hover {
    transform: translateY(-10px) scale(1.02);
    background: rgba(35, 35, 45, 0.6);
    border-color: rgba(10, 132, 255, 0.5); /* Apple Blue subtle highlight */
}

.rewind-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    color: var(--accent-color);
}
.rewind-icon svg {
    width: 28px;
    height: 28px;
}

.rewind-card h3 {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: #fff;
    font-family: var(--font-display);
}
.rewind-card p {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.6);
    margin: 0 0 24px 0;
    min-height: 40px;
}

.rewind-select {
    width: 100%;
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.15);
    color: #fff;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 1rem;
    margin-bottom: 20px;
    outline: none;
    appearance: none;
    cursor: pointer;
    font-family: var(--font-sans);
}
.rewind-select:focus {
    border-color: var(--accent-color);
}
.rewind-select option {
    background: #111;
    color: #fff;
}

.rewind-play-btn {
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    transition: transform 0.2s, filter 0.2s;
}
.rewind-play-btn:active {
    transform: scale(0.95);
}
.rewind-card .btn-primary {
    background: var(--accent-color);
    color: #fff;
    box-shadow: 0 4px 15px rgba(10, 132, 255, 0.4);
}
.rewind-card .btn-primary:hover {
    filter: brightness(1.1);
}
.rewind-card .btn-secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
}
.rewind-card .btn-secondary:hover {
    background: rgba(255,255,255,0.15);
}'''

if old_title_css in css:
    css = css.replace(old_title_css, new_title_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("CSS updated with UI cards and morph animation!")
else:
    print("Could not find CSS title block!")
