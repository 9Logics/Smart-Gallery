import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace single hero img with bg-container
old_hero_html = '''<img class="hero-bg" id="thumb-hero" src="" alt="Hero Background">'''
new_hero_html = '''<div class="hero-bg-container" id="hero-bg-container"></div>'''

if old_hero_html in html:
    html = html.replace(old_hero_html, new_hero_html)
else:
    print("Could not find hero html!")

# JS Update
old_js = '''                                document.getElementById('thumb-hero').src = getBestImage('2026', 'cinematic2026');'''
new_js = '''                                const heroContainer = document.getElementById('hero-bg-container');
                                heroContainer.innerHTML = '';
                                
                                // Pick 3 unique images for the blended collage if possible
                                let heroImages = [];
                                let attempts = 0;
                                while(heroImages.length < 3 && attempts < 20) {
                                    let candidate = galleryPhotos.length > 0 ? galleryPhotos[Math.floor(Math.random() * galleryPhotos.length)] : `https://picsum.photos/seed/hero${attempts}/800/600`;
                                    if (!heroImages.includes(candidate)) heroImages.push(candidate);
                                    attempts++;
                                }
                                // Fallback to duplicates if gallery is too small
                                while(heroImages.length < 3) heroImages.push(heroImages[0]);
                                
                                heroImages.forEach((src, idx) => {
                                    let div = document.createElement('div');
                                    div.className = `hero-collage-item hero-collage-${idx+1}`;
                                    div.style.backgroundImage = `url('${src}')`;
                                    heroContainer.appendChild(div);
                                });'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=268', 'v=269')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS for Hero Collage!")
else:
    print("Could not find JS block!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# CSS Updates
old_hero_css = '''/* Hero Card */
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
}'''

new_hero_css = '''/* Hero Card */
.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 380px; /* Much taller to eliminate negative space */
    background: linear-gradient(135deg, #2c2c2e, #1c1c1e);
    border-radius: 32px;
    overflow: hidden;
    margin-bottom: 32px; 
    flex-shrink: 0;
    box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    transition: transform 0.4s ease;
}
.rewind-hero-card:hover {
    transform: scale(1.01);
}

/* Cinematic Blended Collage */
.hero-bg-container {
    position: absolute;
    inset: 0;
    display: flex;
    transition: transform 1.5s ease;
}
.rewind-hero-card:hover .hero-bg-container {
    transform: scale(1.03);
}
.hero-collage-item {
    position: absolute;
    top: 0;
    height: 100%;
    background-size: cover;
    background-position: center;
    opacity: 0.8;
}
.hero-collage-1 {
    left: 0; width: 40%;
    -webkit-mask-image: linear-gradient(to right, black 70%, transparent 100%);
    mask-image: linear-gradient(to right, black 70%, transparent 100%);
}
.hero-collage-2 {
    left: 30%; width: 40%;
    -webkit-mask-image: linear-gradient(to right, transparent 0%, black 30%, black 70%, transparent 100%);
    mask-image: linear-gradient(to right, transparent 0%, black 30%, black 70%, transparent 100%);
}
.hero-collage-3 {
    left: 60%; width: 40%;
    -webkit-mask-image: linear-gradient(to right, transparent 0%, black 30%, black 100%);
    mask-image: linear-gradient(to right, transparent 0%, black 30%, black 100%);
}'''

if old_hero_css in css:
    css = css.replace(old_hero_css, new_hero_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed CSS for Hero Collage!")
else:
    print("Could not find CSS hero block!")
