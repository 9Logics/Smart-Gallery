import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Smart Thumbnail Matching JS
old_js = '''                                // Populate new dashboard thumbnails
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                const getFallback = (i) => `https://picsum.photos/seed/smartgallery${i}/800/600`;
                                
                                document.getElementById('thumb-hero').src = gallery.length > 0 ? gallery[Math.floor(Math.random() * gallery.length)] : getFallback(0);
                                
                                document.querySelectorAll('.rewind-mini-card img').forEach((img, i) => {
                                    img.src = gallery.length > 0 ? gallery[Math.floor(Math.random() * gallery.length)] : getFallback(i + 1);
                                });'''

new_js = '''                                // Smart Thumbnail Assignment
                                const photoCards = Array.from(document.querySelectorAll('.photo-card'));
                                const gallery = photoCards.map(c => c.querySelector('img')?.src).filter(Boolean);
                                
                                const getBestImage = (keyword, seed) => {
                                    // 1. Check if user's gallery has an image matching the month/year text
                                    const match = photoCards.find(card => card.innerText.includes(keyword));
                                    if (match && match.querySelector('img')) return match.querySelector('img').src;
                                    // 2. Fallback to random user photo
                                    if (gallery.length > 0) return gallery[Math.floor(Math.random() * gallery.length)];
                                    // 3. Fallback to high-quality seeded stock photo
                                    return `https://picsum.photos/seed/${seed}/800/600`;
                                };
                                
                                document.getElementById('thumb-hero').src = getBestImage('2026', 'cinematic2026');
                                
                                document.querySelectorAll('.rewind-mini-card').forEach(card => {
                                    const overlayText = card.querySelector('.mini-overlay').innerText;
                                    card.querySelector('img').src = getBestImage(overlayText, overlayText);
                                });'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=265', 'v=266')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS for Smart Thumbnails!")
else:
    print("Could not find JS block!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Fade away title instead of morphing
old_title_morph = '''.recap-container.options-active .rolling-text-title {
    transform: translateY(-44vh) scale(0.45);
}'''
new_title_morph = '''.recap-container.options-active .rolling-text-title {
    opacity: 0;
    transform: scale(1.1);
    pointer-events: none;
}'''
css = css.replace(old_title_morph, new_title_morph)

old_title_base = '''.rolling-text-title {
    font-size: 6rem;
    font-weight: 800;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
    margin: 0;
    display: flex;
    transition: transform 1s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: center center;
    z-index: 20;
}'''
new_title_base = '''.rolling-text-title {
    font-size: 6rem;
    font-weight: 800;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    letter-spacing: -0.02em;
    margin: 0;
    display: flex;
    transition: opacity 1s ease, transform 1s cubic-bezier(0.16, 1, 0.3, 1);
    transform-origin: center center;
    z-index: 20;
}'''
css = css.replace(old_title_base, new_title_base)

# 2. Update typography to system-ui (Inter/SF Pro) for dashboard and adjust height
old_dash = '''.rewind-dashboard {
    position: absolute;
    top: 10vh; /* Starts higher up */
    left: 0;
    width: 100vw;
    height: 90vh; /* Takes full remaining height */'''
new_dash = '''.rewind-dashboard {
    position: absolute;
    top: 5vh; /* Starts higher since title is gone */
    left: 0;
    width: 100vw;
    height: 95vh; /* Takes full remaining height */
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'''
css = css.replace(old_dash, new_dash)

# Hero Font
old_hero_font = '''font-family: var(--font-display);'''
new_hero_font = '''font-family: inherit;'''
css = css.replace('.hero-overlay h3 {\n    font-size: 3rem;\n    font-weight: 800;\n    margin: 0;\n    color: #fff;\n    ' + old_hero_font, 
                  '.hero-overlay h3 {\n    font-size: 3rem;\n    font-weight: 800;\n    margin: 0;\n    color: #fff;\n    ' + new_hero_font)

old_hero_p_font = '''font-family: var(--font-sans);'''
css = css.replace('.hero-overlay p {\n    font-size: 1.2rem;\n    color: rgba(255,255,255,0.7);\n    margin: 8px 0 24px 0;\n    ' + old_hero_p_font,
                  '.hero-overlay p {\n    font-size: 1.2rem;\n    color: rgba(255,255,255,0.7);\n    margin: 8px 0 24px 0;\n    ' + new_hero_font)

# Section Headers
css = css.replace('.rewind-section h4 {\n    font-size: 1.5rem;\n    font-weight: 700;\n    color: #fff;\n    margin: 0 0 20px 0;\n    ' + old_hero_font,
                  '.rewind-section h4 {\n    font-size: 1.5rem;\n    font-weight: 700;\n    color: #fff;\n    margin: 0 0 20px 0;\n    ' + new_hero_font)

# Mini Overlays
css = css.replace('.mini-overlay {\n    position: absolute;\n    inset: 0;\n    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 60%);\n    display: flex;\n    align-items: flex-end;\n    padding: 20px;\n    font-size: 1.3rem;\n    font-weight: 700;\n    color: #fff;\n    ' + old_hero_p_font,
                  '.mini-overlay {\n    position: absolute;\n    inset: 0;\n    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 60%);\n    display: flex;\n    align-items: flex-end;\n    padding: 20px;\n    font-size: 1.3rem;\n    font-weight: 700;\n    color: #fff;\n    ' + new_hero_font)


with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed CSS fonts and title fade out!")
