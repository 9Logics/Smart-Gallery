import re

# 1. Add #slide-hero to index.html
html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

new_slide = r'''          <div class="recap-slide siena-depth" id="slide-hero">
                <div class="siena-layer" data-depth="20" style="text-align: center; margin-bottom: 20px;">
                    <h2 style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 2.5rem; text-shadow: 4px 4px 0px #111;">A moment worth remembering</h2>
                </div>
                <div id="hero-moment-container" class="siena-layer hero-glow-border" data-depth="60">
                    <img id="hero-moment-img" src="" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />
                </div>
            </div>
        </div>'''
        
old_end = r"</div>\n        </div>\n        \n        <div class=\"recap-nav-left\""
new_end = new_slide + "\n        \n        <div class=\"recap-nav-left\""

if 'id="slide-hero"' not in html_code:
    html_code = re.sub(r'</div>\s*</div>\s*<div class="recap-nav-left"', new_slide + '\n        \n        <div class="recap-nav-left"', html_code)
    html_code = html_code.replace("v=313", "v=314")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)


# 2. Add hero logic to recap_player.js
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Update sequence length to 6 slides
js_code = js_code.replace("recapCurrentSlide >= 5", "recapCurrentSlide >= 6")

# Add fetch logic for memorable_moment and montage
old_fetch_end = r"document\.getElementById\('slide-place'\)\.style\.display = 'none'; // skip\n              \}"
new_fetch_end = '''document.getElementById('slide-place').style.display = 'none'; // skip
              }
              
              if (data.memorable_moment) {
                  document.getElementById('hero-moment-img').src = `/api/photo/file/${encodeURIComponent(data.memorable_moment)}`;
              } else {
                  document.getElementById('slide-hero').style.display = 'none';
              }
              
              // Populate Montage Burst (Slide 0)
              const montageContainer = document.getElementById('montage-container');
              if (montageContainer && data.gallery_photos) {
                  montageContainer.innerHTML = '';
                  let burstPhotos = data.gallery_photos.slice(0, 8); // up to 8 photos
                  burstPhotos.forEach((p, idx) => {
                      let div = document.createElement('div');
                      div.className = 'montage-burst-photo';
                      div.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(p)}')`;
                      
                      let r = (Math.random() - 0.5) * 40;
                      let dx = (Math.random() - 0.5) * 300;
                      let dy = (Math.random() - 0.5) * 300;
                      div.style.setProperty('--target-rot', `${r}deg`);
                      div.style.setProperty('--target-x', `${dx}px`);
                      div.style.setProperty('--target-y', `${dy}px`);
                      div.style.animationDelay = `${idx * 150}ms`; // Stagger entrance
                      
                      montageContainer.appendChild(div);
                  });
              }'''
              
if "hero-moment-img" not in js_code:
    js_code = re.sub(old_fetch_end, new_fetch_end, js_code)


# Trigger animations when slide is active
old_trans = r"// Simple swap for fallback\n    slides\.forEach\(\(s, i\) => \{"
new_trans = '''// Custom triggers for specific slides
    if (slideIndex === 0) {
        // Retrigger montage burst
        document.querySelectorAll('.montage-burst-photo').forEach(el => {
            el.style.animation = 'none';
            void el.offsetWidth;
            el.style.animation = 'throwOn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards';
            el.style.animationDelay = el.style.animationDelay || '0ms';
        });
    }
    
    // Simple swap for fallback
    slides.forEach((s, i) => {'''

if "Retrigger montage burst" not in js_code:
    js_code = js_code.replace("// Simple swap for fallback\n    slides.forEach((s, i) => {", new_trans)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)


# 3. Add CSS to style.css
css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

new_css = '''
/* --- Phase D: Montage & Hero Moment --- */
#montage-container {
    position: relative;
    width: 100vw;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.montage-burst-photo {
    position: absolute;
    width: 250px;
    height: 250px;
    background-size: cover;
    background-position: center;
    border: 8px solid #fff;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    opacity: 0;
    transform: scale(0.1) translate(0,0) rotate(-45deg);
}

@keyframes throwOn {
    0% { transform: scale(0.1) translate(0,0) rotate(-45deg); opacity: 0; }
    60% { transform: scale(1.1) translate(var(--target-x), var(--target-y)) rotate(var(--target-rot)); opacity: 1; }
    100% { transform: scale(1) translate(var(--target-x), var(--target-y)) rotate(var(--target-rot)); opacity: 1; }
}

.hero-glow-border {
    position: relative;
    width: 60vmin;
    height: 60vmin;
    margin: 0 auto;
    padding: 6px;
    border-radius: 12px;
    background: linear-gradient(45deg, #ff0a54, #ff6b35, #ffd700, #00d4ff, #ff0a54);
    background-size: 300% 300%;
    animation: gradientSpin 4s ease infinite;
    box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 100px rgba(255, 10, 84, 0.4);
    transition: transform 0.3s ease-out;
}

@keyframes gradientSpin {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
'''
if "montage-burst-photo" not in css_code:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(new_css)

print("Applied Phase D (Montage Burst & Hero Moment).")
