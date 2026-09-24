import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace old rewind-options with the new Netflix-style dashboard
old_options_start = '<div class="rewind-options" id="rewind-options">'
old_options_end = '</div>\n    </div>\n\n    <script>'
start_idx = html.find(old_options_start)
end_idx = html.find(old_options_end)

new_html = '''<div class="rewind-dashboard" id="rewind-dashboard">
            <!-- Hero: 2026 Recap -->
            <div class="rewind-hero-card">
                <img class="hero-bg" id="thumb-hero" src="" alt="Hero Background">
                <div class="hero-overlay">
                    <h3>2026 Recap</h3>
                    <p>Your entire year in a cinematic journey</p>
                    <button class="btn btn-primary rewind-play-btn">Play Rewind</button>
                </div>
            </div>
            
            <div class="rewind-section-group">
                <!-- Monthly Row -->
                <div class="rewind-section">
                    <h4>Monthly Rewinds</h4>
                    <div class="rewind-row" id="monthly-row">
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">August</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">July</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">June</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">May</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">April</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">March</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">February</div></div>
                        <div class="rewind-mini-card"><img src=""/><div class="mini-overlay">January</div></div>
                    </div>
                </div>

                <!-- Past Years Row -->
                <div class="rewind-section">
                    <h4>Past Years</h4>
                    <div class="rewind-row" id="past-row">
                        <div class="rewind-mini-card year-card"><img src=""/><div class="mini-overlay">2025</div></div>
                        <div class="rewind-mini-card year-card"><img src=""/><div class="mini-overlay">2024</div></div>
                        <div class="rewind-mini-card year-card"><img src=""/><div class="mini-overlay">2023</div></div>
                    </div>
                </div>
            </div>
        </div>
'''

if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + new_html + html[end_idx:]

# Update JS to populate the new images
old_js_lucide = '''                                // Populate thumbnails with random images
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                if (gallery.length > 2) {
                                    document.getElementById('thumb-1').src = gallery[Math.floor(Math.random() * gallery.length)];
                                    document.getElementById('thumb-2').src = gallery[Math.floor(Math.random() * gallery.length)];
                                    document.getElementById('thumb-3').src = gallery[Math.floor(Math.random() * gallery.length)];
                                }'''
new_js_lucide = '''                                // Populate new dashboard thumbnails
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                if (gallery.length > 0) {
                                    document.getElementById('thumb-hero').src = gallery[Math.floor(Math.random() * gallery.length)];
                                    document.querySelectorAll('.rewind-mini-card img').forEach(img => {
                                        img.src = gallery[Math.floor(Math.random() * gallery.length)];
                                    });
                                }'''

if old_js_lucide in html:
    html = html.replace(old_js_lucide, new_js_lucide)

html = html.replace('document.getElementById(\'recap-container\').classList.add(\'options-active\');', 
                    'document.getElementById(\'recap-container\').classList.add(\'options-active\');\n                                document.getElementById(\'rewind-dashboard\').classList.add(\'active\');')
html = html.replace('v=259', 'v=260')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML Updated to Dashboard UI")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace old cards CSS with Dashboard CSS
old_css_start = '.rewind-options {'
old_css_end = '.rewind-card .btn-secondary:hover {\n    background: rgba(255,255,255,0.15);\n    border-color: rgba(255,255,255,0.25);\n}'
start_c = css.find(old_css_start)
end_c = css.find(old_css_end) + len(old_css_end)

new_css = '''/* Rewind Dashboard UI */
.rewind-dashboard {
    position: absolute;
    top: 15vh; /* Starts right below the title */
    left: 0;
    width: 100vw;
    height: 85vh;
    padding: 0 5%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transform: translateY(40px);
    z-index: 19;
    overflow-y: auto;
    overflow-x: hidden;
    padding-bottom: 60px;
}

.rewind-dashboard.active {
    opacity: 1;
    pointer-events: all;
    transform: translateY(0);
}

/* Custom Scrollbar for dashboard */
.rewind-dashboard::-webkit-scrollbar {
    width: 8px;
}
.rewind-dashboard::-webkit-scrollbar-track {
    background: transparent;
}
.rewind-dashboard::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 4px;
}

/* Hero Card */
.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 300px; /* Big cinematic hero */
    border-radius: 32px;
    overflow: hidden;
    margin-bottom: 40px;
    flex-shrink: 0;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    transition: transform 0.4s ease;
}
.rewind-hero-card:hover {
    transform: scale(1.01);
}
.hero-bg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    top: 0;
    left: 0;
    transition: transform 1s ease;
}
.rewind-hero-card:hover .hero-bg {
    transform: scale(1.03);
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(5,5,5,0.9) 0%, rgba(5,5,5,0.2) 60%, transparent 100%);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 40px;
}
.hero-overlay h3 {
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
    color: #fff;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
}
.hero-overlay p {
    font-size: 1.2rem;
    color: rgba(255,255,255,0.7);
    margin: 8px 0 24px 0;
    font-family: var(--font-sans);
}
.rewind-play-btn {
    width: fit-content;
    padding: 16px 40px;
    border-radius: 100px;
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
    border: none;
    background: #fff;
    color: #000;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s, box-shadow 0.2s;
    font-family: var(--font-sans);
    box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
}
.rewind-play-btn:active {
    transform: scale(0.95);
}
.rewind-play-btn:hover {
    background: #e0e0e0;
    box-shadow: 0 12px 32px rgba(255, 255, 255, 0.3);
}

/* Section Groups */
.rewind-section-group {
    display: flex;
    flex-direction: column;
    gap: 40px;
}

.rewind-section {
    display: flex;
    flex-direction: column;
}
.rewind-section h4 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 20px 0;
    font-family: var(--font-display);
    padding-left: 10px;
}

/* Horizontal Scroll Rows */
.rewind-row {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding: 10px;
    /* Hide scrollbar for clean look */
    -ms-overflow-style: none;
    scrollbar-width: none;
    scroll-snap-type: x mandatory;
}
.rewind-row::-webkit-scrollbar {
    display: none;
}

/* Mini Cards */
.rewind-mini-card {
    position: relative;
    width: 220px;
    height: 140px;
    flex-shrink: 0;
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    scroll-snap-align: start;
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s;
}
.rewind-mini-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 16px 32px rgba(0,0,0,0.6);
}
.rewind-mini-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.8s ease;
}
.rewind-mini-card:hover img {
    transform: scale(1.05);
}
.mini-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 60%);
    display: flex;
    align-items: flex-end;
    padding: 20px;
    font-size: 1.3rem;
    font-weight: 700;
    color: #fff;
    font-family: var(--font-sans);
}

.year-card {
    width: 280px;
    height: 180px;
}
.year-card .mini-overlay {
    font-size: 1.8rem;
}
'''

if start_c != -1 and end_c != -1:
    css = css[:start_c] + new_css + css[end_c:]
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("CSS Updated to Dashboard UI")
else:
    print("Could not find old css")
