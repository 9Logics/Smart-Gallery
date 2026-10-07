import re

# 1. Update style.css for true aspect ratio
css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

# Replace person and place fan photo container styles
css_code = re.sub(
    r"\.(person|place)-fan-photo\s*\{[^}]+\}",
    r".\1-fan-photo {\n    position: absolute;\n    width: max-content;\n    height: max-content;\n    max-width: 400px;\n    max-height: 50vh;\n    background: #fff;\n    padding: 12px 12px 50px 12px;\n    border-radius: 6px;\n    box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,0,0,0.1) inset;\n    transition: transform 0.6s cubic-bezier(0.2, 1.2, 0.4, 1);\n    transform-origin: bottom center;\n}",
    css_code
)

# Replace person and place fan photo img styles
css_code = re.sub(
    r"\.(person|place)-fan-photo img\s*\{[^}]+\}",
    r".\1-fan-photo img {\n    max-width: 100%;\n    max-height: calc(50vh - 62px);\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    display: block;\n    border-radius: 3px;\n    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);\n}",
    css_code
)

# Hero moment container
css_code = re.sub(
    r"\.hero-glow-border\s*\{[^}]+\}",
    r".hero-glow-border {\n    position: relative;\n    width: max-content;\n    height: max-content;\n    max-width: 80vw;\n    max-height: 70vh;\n    margin: 0 auto;\n    padding: 6px;\n    border-radius: 12px;\n    background: linear-gradient(45deg, #ff0a54, #ff6b35, #ffd700, #00d4ff, #ff0a54);\n    background-size: 300% 300%;\n    animation: gradientSpin 4s ease infinite;\n    box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 100px rgba(255, 10, 84, 0.4);\n    transition: transform 0.3s ease-out;\n}",
    css_code
)

if "#hero-moment-img {" not in css_code:
    css_code += "\n#hero-moment-img {\n    max-width: calc(80vw - 12px);\n    max-height: calc(70vh - 12px);\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    border-radius: 8px;\n    display: block;\n}\n"

# Montage burst container
css_code = re.sub(
    r"\.montage-burst-photo\s*\{[^}]+\}",
    r".montage-burst-photo {\n    position: absolute;\n    width: max-content;\n    height: max-content;\n    max-width: 30vh;\n    max-height: 30vh;\n    background: #fff;\n    padding: 8px 8px 24px 8px;\n    border-radius: 4px;\n    box-shadow: 0 10px 30px rgba(0,0,0,0.5);\n    opacity: 0;\n    transform: scale(0.1) translate(0,0) rotate(-45deg);\n}",
    css_code
)

if ".montage-burst-photo img" not in css_code:
    css_code += "\n.montage-burst-photo img {\n    max-width: 100%;\n    max-height: calc(30vh - 32px);\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    display: block;\n    border-radius: 2px;\n}\n"

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_code)


# 2. Update recap_player.js for high-res urls & Promise.all preloading
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Change Cycling Deck URLs to high-res /api/photo/file/
js_code = js_code.replace(
    r"div.innerHTML = `<img src=\"/api/photo/thumbnail/${encodeURIComponent(p)}\" />`;",
    r"div.innerHTML = `<img src=\"/api/photo/file/${encodeURIComponent(p)}\" />`;"
)

# Change Montage burst from background-image to an actual <img> tag for true aspect ratio
old_burst = r'''burst.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(photoPath)}')`;'''
new_burst = r'''burst.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(photoPath)}" />`;'''
js_code = js_code.replace(old_burst, new_burst)

# Now, implement Promise.all preloader
# We want to wait for all the high-res images to load before dismissing the preloader.
# Find the preloader dismissal: `preloader.classList.add('slide-up');`
old_dismissal = '''            preloader.classList.add('slide-up');
                
            // Show slides
            document.getElementById('recap-slides-container').classList.remove('hidden');
            
            // Remove clone
            clone.remove();
            element.style.opacity = '1';
            
            // Init sequence
            recapCurrentSlide = 0;
            recapSlides = Array.from(document.querySelectorAll('.recap-slide')).filter(s => s.style.display !== 'none');
            showRecapSlide(0);
            
            isRecapLoading = false;
        }, 600);'''

new_dismissal = '''            // PRELOADER: Wait for all high-res main images to download
            let preloadUrls = [];
            
            if (data.top_person_photos) preloadUrls = preloadUrls.concat(data.top_person_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
            if (data.top_person_feature) preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.top_person_feature)}`);
            if (data.iconic_place_photos) preloadUrls = preloadUrls.concat(data.iconic_place_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
            if (data.memorable_moment) preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.memorable_moment)}`);
            if (data.gallery_photos) preloadUrls = preloadUrls.concat(data.gallery_photos.slice(0,8).map(p => `/api/photo/file/${encodeURIComponent(p)}`));
            
            // Deduplicate
            preloadUrls = [...new Set(preloadUrls)];
            
            let loadPromises = preloadUrls.map(url => {
                return new Promise((resolve) => {
                    const img = new Image();
                    img.onload = resolve;
                    img.onerror = resolve; // Continue even if one fails
                    img.src = url;
                });
            });
            
            // Ensure preloader runs for at least 800ms for visual FLIP transition to settle
            let timerPromise = new Promise(resolve => setTimeout(resolve, 800));
            loadPromises.push(timerPromise);
            
            document.querySelector('.preloader-text').innerText = "Developing photos...";
            
            Promise.all(loadPromises).then(() => {
                preloader.classList.add('slide-up');
                    
                // Show slides
                document.getElementById('recap-slides-container').classList.remove('hidden');
                
                // Remove clone
                if (clone) clone.remove();
                element.style.opacity = '1';
                
                // Init sequence
                recapCurrentSlide = 0;
                recapSlides = Array.from(document.querySelectorAll('.recap-slide')).filter(s => s.style.display !== 'none');
                showRecapSlide(0);
                
                isRecapLoading = false;
            });
            
        }, 600);'''

js_code = js_code.replace(old_dismissal, new_dismissal)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print("Applied aspect ratio logic and full-quality Promise.all preloader.")
