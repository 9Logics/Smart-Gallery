import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace SVG fallback with beautiful Unsplash/Picsum placeholder thumbnails
old_js = '''                                // Populate new dashboard thumbnails
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                const getFallback = (i) => `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='400'%3E%3Cdefs%3E%3ClinearGradient id='g${i}' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')}'/%3E%3Cstop offset='100%25' stop-color='%23${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')}'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='100%25' height='100%25' fill='url(%23g${i})'/%3E%3C/svg%3E`;'''

new_js = '''                                // Populate new dashboard thumbnails
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                const getFallback = (i) => `https://picsum.photos/seed/smartgallery${i}/800/600`;'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=263', 'v=264')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS Fallbacks to Picsum!")
else:
    print("Could not find JS Fallback block!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Adjust title morph to be higher up
old_morph = '''.recap-container.options-active .rolling-text-title {
    transform: translateY(-38vh) scale(0.45);
}'''
new_morph = '''.recap-container.options-active .rolling-text-title {
    transform: translateY(-44vh) scale(0.45);
}'''
css = css.replace(old_morph, new_morph)

# 2. Adjust Dashboard scaling and gaps so it fits strictly in 100vh
old_dash = '''.rewind-dashboard {
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
}'''
new_dash = '''.rewind-dashboard {
    position: absolute;
    top: 10vh; /* Starts higher up */
    left: 0;
    width: 100vw;
    height: 90vh; /* Takes full remaining height */
    padding: 0 5%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transform: translateY(40px);
    z-index: 19;
    overflow: hidden; /* Prevent vertical scrolling */
}'''
css = css.replace(old_dash, new_dash)

# Shrink the hero card and adjust gaps
old_hero = '''/* Hero Card */
.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 300px; /* Big cinematic hero */
    background: linear-gradient(135deg, #2c2c2e, #1c1c1e); /* Base color */
    border-radius: 32px;
    overflow: hidden;
    margin-bottom: 40px;
    flex-shrink: 0;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    transition: transform 0.4s ease;
}'''
new_hero = '''/* Hero Card */
.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 240px; /* Reduced height to fit everything in 1 screen */
    background: linear-gradient(135deg, #2c2c2e, #1c1c1e);
    border-radius: 32px;
    overflow: hidden;
    margin-bottom: 20px; /* Reduced bottom margin */
    flex-shrink: 0;
    box-shadow: 0 16px 40px rgba(0,0,0,0.5);
    transition: transform 0.4s ease;
}'''
css = css.replace(old_hero, new_hero)

# Reduce section gaps
old_group = '''.rewind-section-group {
    display: flex;
    flex-direction: column;
    gap: 40px;
}'''
new_group = '''.rewind-section-group {
    display: flex;
    flex-direction: column;
    gap: 16px; /* Tighter gap so everything fits without scrolling */
}'''
css = css.replace(old_group, new_group)

# Adjust row padding and past-years height slightly
old_year = '''.year-card {
    width: 280px;
    height: 180px;
}'''
new_year = '''.year-card {
    width: 280px;
    height: 140px; /* Match monthly height to save vertical space */
}'''
css = css.replace(old_year, new_year)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed CSS vertical scaling!")
