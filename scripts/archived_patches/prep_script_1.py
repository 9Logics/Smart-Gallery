import re

# 1. Update style.css for true aspect ratio
css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

# person-fan-photo & place-fan-photo
css_code = re.sub(
    r"\.(person|place)-fan-photo\s*\{[^}]+\}",
    r".\1-fan-photo {\n    position: absolute;\n    width: max-content;\n    height: max-content;\n    max-width: 400px;\n    max-height: 50vh;\n    background: #fff;\n    padding: 12px 12px 50px 12px;\n    border-radius: 6px;\n    box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,0,0,0.1) inset;\n    transition: transform 0.6s cubic-bezier(0.2, 1.2, 0.4, 1);\n    transform-origin: bottom center;\n}",
    css_code
)

css_code = re.sub(
    r"\.(person|place)-fan-photo img\s*\{[^}]+\}",
    r".\1-fan-photo img {\n    max-width: 100%;\n    max-height: calc(50vh - 62px);\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    display: block;\n    border-radius: 3px;\n    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);\n}",
    css_code
)

css_code = re.sub(
    r"\.person-fan-photo\.feature-photo\s*\{[^}]+\}",
    r".person-fan-photo.feature-photo {\n    border: 4px solid #FF0A54;\n    z-index: 10;\n}",
    css_code
)

# hero moment
css_code = re.sub(
    r"\.hero-glow-border\s*\{[^}]+\}",
    r".hero-glow-border {\n    position: relative;\n    width: max-content;\n    height: max-content;\n    max-width: 80vw;\n    max-height: 70vh;\n    margin: 0 auto;\n    padding: 6px;\n    border-radius: 12px;\n    background: linear-gradient(45deg, #ff0a54, #ff6b35, #ffd700, #00d4ff, #ff0a54);\n    background-size: 300% 300%;\n    animation: gradientSpin 4s ease infinite;\n    box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 100px rgba(255, 10, 84, 0.4);\n    transition: transform 0.3s ease-out;\n}",
    css_code
)

if "#hero-moment-img {" not in css_code:
    css_code += "\n#hero-moment-img {\n    max-width: calc(80vw - 12px);\n    max-height: calc(70vh - 12px);\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    border-radius: 8px;\n    display: block;\n}\n"

# montage burst
css_code = re.sub(
    r"\.montage-burst-photo\s*\{[^}]+\}",
    r".montage-burst-photo {\n    position: absolute;\n    width: max-content;\n    height: max-content;\n    max-width: 30vh;\n    max-height: 30vh;\n    background: #fff;\n    padding: 8px 8px 24px 8px;\n    border-radius: 4px;\n    box-shadow: 0 10px 30px rgba(0,0,0,0.5);\n    opacity: 0;\n    transform: scale(0.1) translate(0,0) rotate(-45deg);\n}",
    css_code
)

if ".montage-burst-photo img" not in css_code:
    css_code += "\n.montage-burst-photo img {\n    max-width: 100%;\n    max-height: calc(30vh - 32px);\n    width: auto;\n    height: auto;\n    object-fit: contain;\n    display: block;\n    border-radius: 2px;\n}\n"

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_code)


# 2. Update recap_player.js for high-res urls & preloading
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Change URLs to high-res /api/photo/file/
js_code = js_code.replace(
    r"div.innerHTML = `<img src=\"/api/photo/thumbnail/${encodeURIComponent(p)}\" />`;",
    r"div.innerHTML = `<img src=\"/api/photo/file/${encodeURIComponent(p)}\" />`;"
)

# We need to change montage burst to use <img> instead of background-image
old_burst = r'''burst\.style\.backgroundImage = `url\('/api/photo/thumbnail/\$\{encodeURIComponent\(photoPath\)\}'\)`;'''
new_burst = r'''burst.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(photoPath)}" />`;'''
js_code = re.sub(old_burst, new_burst, js_code)

# Now, implement the preloader logic in openRecapPlayer()
# Look for the section after recapData = data;
old_preloader = r'''// We don't populate numbers yet, we animate them on slide load
            
            
            document\.getElementById\('recap-stat-person'\)\.innerText = data\.top_person \|\| "Yourself!";
            createCyclingDeck\('person-photos-fan', data\.top_person_photos, data\.top_person_feature\);

            
            if \(data\.iconic_place\) \{
                document\.getElementById\('recap-stat-place'\)\.innerText = data\.iconic_place;
                
                createCyclingDeck\('place-photos-fan', data\.iconic_place_photos, null\);
            \} else \{
                document\.getElementById\('slide-place'\)\.style\.display = 'none'; // skip
            \}
            
            // Skiper 30 Parallax Gallery - Massive Scatter.*?gallery\.appendChild\(img\);
                \}\);
            \}
            
            if \(data\.memorable_moment\) \{
                let mmImg = document\.getElementById\('hero-moment-img'\);
                if \(mmImg\) mmImg\.src = `/api/photo/file/\$\{encodeURIComponent\(data\.memorable_moment\)\}`;
            \} else \{
                let sh = document\.getElementById\('slide-hero'\);
                if \(sh\) sh\.style\.display = 'none';
            \}
            
            // Populate Montage Burst \(Slide 0\)
            const montageContainer = document\.getElementById\('montage-container'\);
            if \(montageContainer && data\.gallery_photos\) \{
                montageContainer\.innerHTML = '';
                let burstPhotos = data\.gallery_photos\.slice\(0, 8\); // up to 8 photos
                burstPhotos\.forEach\(\(photoPath, idx\) => \{
                    const burst = document\.createElement\('div'\);
                    burst\.className = 'montage-burst-photo';
                    burst\.innerHTML = `<img src="/api/photo/file/\$\{encodeURIComponent\(photoPath\)\}" />`;
                    montageContainer\.appendChild\(burst\);.*?setTimeout\(\(\) => \{
                                        nextRecapSlide\(\);
                                    \}, 600\); // Wait for scatter animation
                                \}, 3000\); // Hold on screen for 3s
                            \}
                        \}, idx \* 150\);
                    \}\);
            \}

            preloader\.classList\.add\('slide-up'\);
                
            // Show slides
            document\.getElementById\('recap-slides-container'\)\.classList\.remove\('hidden'\);
            
            // Remove clone
            clone\.remove\(\);
            element\.style\.opacity = '1';
            
            // Init sequence
            recapCurrentSlide = 0;
            recapSlides = Array\.from\(document\.querySelectorAll\('\.recap-slide'\)\)\.filter\(s => s\.style\.display !== 'none'\);
            showRecapSlide\(0\);
            
            isRecapLoading = false;
        \}, 600\);'''

# Because regex replacement on massive blocks is fragile, I'll extract the exact lines I want to replace using a cleaner approach.
