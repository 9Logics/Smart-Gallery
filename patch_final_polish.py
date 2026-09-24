import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Fix title cutoff and glow
old_title = '''.rolling-text-title {
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
}'''
new_title = '''.rolling-text-title {
    font-size: 6rem;
    font-weight: 800;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
    margin: 0;
    display: flex;
    transition: transform 1s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: center center;
    z-index: 20;
}
.recap-container.options-active .rolling-text-title {
    transform: translateY(-38vh) scale(0.45);
}'''
css = css.replace(old_title, new_title)

# Fix roll char wrap padding
old_wrap = '''.roll-char-wrap {
    display: inline-block;
    overflow: hidden;
    vertical-align: top;
    /* Extra padding to prevent clipping of the serif tail */
    padding-bottom: 20px;
    margin-bottom: -20px;
}'''
new_wrap = '''.roll-char-wrap {
    display: inline-block;
    overflow: hidden;
    vertical-align: top;
    padding-bottom: 20px;
    margin-bottom: -20px;
    padding-right: 10px; /* Prevent right edge cutoff for italic/wide fonts */
    margin-right: -10px;
}'''
css = css.replace(old_wrap, new_wrap)

# 2. Options UI overhaul (Bigger cards, thumbnails, fixed select, centered buttons)
old_options = '''.rewind-options {
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -15%);
    opacity: 0;
    pointer-events: none;
    display: flex;
    gap: 32px;
    z-index: 19;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transition-delay: 0.3s;
}
.recap-container.options-active .rewind-options {
    opacity: 1;
    pointer-events: all;
    transform: translate(-50%, -45%);
}

.rewind-card {
    background: rgba(20, 20, 30, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 32px;
    padding: 40px 32px;
    width: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    backdrop-filter: blur(40px) saturate(200%);
    transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.15);
}
.rewind-card:hover {
    transform: translateY(-12px) scale(1.03);
    background: rgba(30, 30, 45, 0.7);
    border-color: rgba(10, 132, 255, 0.6);
}

.rewind-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(10,132,255,0.2), rgba(10,132,255,0.05));
    border: 1px solid rgba(10,132,255,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    color: var(--accent-color);
}
.rewind-icon svg {
    width: 32px;
    height: 32px;
}

.rewind-card h3 {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0 0 10px 0;
    color: #fff;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
}
.rewind-card p {
    font-size: 1rem;
    color: rgba(255,255,255,0.5);
    margin: 0 0 32px 0;
    line-height: 1.4;
    min-height: 45px;
    font-family: var(--font-sans);
}

.rewind-select-wrap {
    width: 100%;
    position: relative;
    margin-bottom: 12px;
}
.rewind-select {
    width: 100%;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 1.05rem;
    font-weight: 500;
    outline: none;
    appearance: none;
    cursor: pointer;
    font-family: var(--font-sans);
    transition: border-color 0.2s, background 0.2s;
    text-align: center;
}
.rewind-select:hover {
    background: rgba(255,255,255,0.08);
}
.rewind-select:focus {
    border-color: var(--accent-color);
    background: rgba(255,255,255,0.1);
}
.rewind-select option {
    background: #111;
    color: #fff;
}
/* Down arrow for select */
.rewind-select-wrap::after {
    content: "▼";
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    pointer-events: none;
}

.rewind-play-btn {
    width: 100%;
    padding: 16px;
    border-radius: 16px;
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
    border: none;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s, box-shadow 0.2s;
    font-family: var(--font-sans);
}
.rewind-play-btn:active {
    transform: scale(0.95);
}
.rewind-card .btn-primary {
    background: var(--accent-color);
    color: #fff;
    box-shadow: 0 8px 24px rgba(10, 132, 255, 0.3);
}
.rewind-card .btn-primary:hover {
    background: #1a8eff;
    box-shadow: 0 12px 32px rgba(10, 132, 255, 0.5);
}
.rewind-card .btn-secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.1);
}
.rewind-card .btn-secondary:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.2);
}'''

new_options = '''.rewind-options {
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -15%);
    opacity: 0;
    pointer-events: none;
    display: flex;
    gap: 40px; /* More spacing */
    z-index: 19;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transition-delay: 0.3s;
}
.recap-container.options-active .rewind-options {
    opacity: 1;
    pointer-events: all;
    transform: translate(-50%, -45%);
}

.rewind-card {
    background: rgba(20, 20, 30, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 36px;
    padding: 24px;
    width: 380px; /* Much larger */
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    backdrop-filter: blur(40px) saturate(200%);
    transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.15);
}
.rewind-card:hover {
    transform: translateY(-12px) scale(1.02);
    background: rgba(30, 30, 45, 0.8);
    border-color: rgba(255, 255, 255, 0.2);
}

.rewind-thumbnail {
    width: 100%;
    height: 180px;
    border-radius: 20px;
    background: #000;
    margin-bottom: 24px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}
.rewind-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.8;
    transition: opacity 0.4s ease, transform 1s ease;
}
.rewind-card:hover .rewind-thumbnail img {
    opacity: 1;
    transform: scale(1.05);
}

.rewind-card h3 {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 10px 0;
    color: #fff;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
}
.rewind-card p {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.55);
    margin: 0 0 32px 0;
    line-height: 1.4;
    min-height: 50px;
    font-family: var(--font-sans);
}

.rewind-select-wrap {
    width: 100%;
    margin-bottom: 12px;
}
.rewind-select {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    padding: 16px;
    border-radius: 16px;
    font-size: 1.1rem;
    font-weight: 500;
    outline: none;
    cursor: pointer;
    font-family: var(--font-sans);
    transition: border-color 0.2s, background 0.2s;
    text-align: center;
    text-align-last: center; /* Forces center on native dropdowns */
}
.rewind-select:hover {
    background: rgba(255,255,255,0.08);
}
.rewind-select:focus {
    border-color: var(--accent-color);
    background: rgba(255,255,255,0.1);
}
.rewind-select option {
    background: #111;
    color: #fff;
}

.rewind-play-btn {
    width: 100%;
    box-sizing: border-box;
    padding: 18px;
    border-radius: 16px;
    font-weight: 700;
    font-size: 1.15rem;
    cursor: pointer;
    border: none;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s, box-shadow 0.2s;
    font-family: var(--font-sans);
    display: flex;
    align-items: center;
    justify-content: center; /* Fixes left alignment */
    text-align: center;
}
.rewind-play-btn:active {
    transform: scale(0.95);
}
.rewind-card .btn-primary {
    background: #fff;
    color: #000;
    box-shadow: 0 8px 24px rgba(255, 255, 255, 0.2);
}
.rewind-card .btn-primary:hover {
    background: #f0f0f0;
    box-shadow: 0 12px 32px rgba(255, 255, 255, 0.3);
}
.rewind-card .btn-secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.1);
}
.rewind-card .btn-secondary:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.25);
}'''

css = css.replace(old_options, new_options)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("CSS updated!")

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove text-transform: uppercase from JS text split and change string
old_text = 'const text = "Your Rewinds";'
new_text = 'const text = "Your Rewinds"; // We rely on font-display without uppercase now'
if old_text in html:
    html = html.replace(old_text, new_text)

# Update HTML icons to thumbnails
old_html_cards = '''<div class="rewind-options" id="rewind-options">
            <div class="rewind-card">
                <div class="rewind-icon"><i data-lucide="sparkles"></i></div>'''
new_html_cards = '''<div class="rewind-options" id="rewind-options">
            <div class="rewind-card">
                <div class="rewind-thumbnail"><img id="thumb-1" src="" alt="Rewind"></div>'''
html = html.replace(old_html_cards, new_html_cards)

old_html_card2 = '''<div class="rewind-card">
                <div class="rewind-icon"><i data-lucide="calendar"></i></div>'''
new_html_card2 = '''<div class="rewind-card">
                <div class="rewind-thumbnail"><img id="thumb-2" src="" alt="Month"></div>'''
html = html.replace(old_html_card2, new_html_card2)

old_html_card3 = '''<div class="rewind-card">
                <div class="rewind-icon"><i data-lucide="history"></i></div>'''
new_html_card3 = '''<div class="rewind-card">
                <div class="rewind-thumbnail"><img id="thumb-3" src="" alt="Past"></div>'''
html = html.replace(old_html_card3, new_html_card3)

# Add logic to populate thumbnails
old_js_lucide = '''                                // Re-initialize lucide icons for the new cards
                                if (window.lucide) {
                                    window.lucide.createIcons();
                                }'''
new_js_lucide = '''                                // Populate thumbnails with random images
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                if (gallery.length > 2) {
                                    document.getElementById('thumb-1').src = gallery[Math.floor(Math.random() * gallery.length)];
                                    document.getElementById('thumb-2').src = gallery[Math.floor(Math.random() * gallery.length)];
                                    document.getElementById('thumb-3').src = gallery[Math.floor(Math.random() * gallery.length)];
                                }'''
html = html.replace(old_js_lucide, new_js_lucide)

html = html.replace('v=258', 'v=259')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML updated!")
