import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Replace the heroImg.src logic with the collage logic
old_js = """                const heroImg = document.getElementById('hero-moment-img');
                if (heroImg) {
                    heroImg.src = imgUrl;
                }"""

new_js = """                const heroContainer = document.getElementById('hero-moment-container');
                if (heroContainer) {
                    heroContainer.innerHTML = '';
                    const mPhotos = data.moment_photos && data.moment_photos.length > 0 ? data.moment_photos : (data.memorable_moment ? [data.memorable_moment] : []);
                    
                    if (mPhotos.length === 1) {
                        heroContainer.innerHTML = `<img src="/api/photo/file/${encodeURIComponent(mPhotos[0])}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                    } else if (mPhotos.length === 2) {
                        heroContainer.style.display = 'grid';
                        heroContainer.style.gridTemplateColumns = '1fr 1fr';
                        heroContainer.style.gap = '8px';
                        mPhotos.forEach(p => {
                            heroContainer.innerHTML += `<img src="/api/photo/file/${encodeURIComponent(p)}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                        });
                    } else if (mPhotos.length === 3) {
                        heroContainer.style.display = 'grid';
                        heroContainer.style.gridTemplateColumns = '2fr 1fr';
                        heroContainer.style.gridTemplateRows = '1fr 1fr';
                        heroContainer.style.gap = '8px';
                        heroContainer.innerHTML += `<img src="/api/photo/file/${encodeURIComponent(mPhotos[0])}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px; grid-row: span 2;" />`;
                        heroContainer.innerHTML += `<img src="/api/photo/file/${encodeURIComponent(mPhotos[1])}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                        heroContainer.innerHTML += `<img src="/api/photo/file/${encodeURIComponent(mPhotos[2])}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                    } else if (mPhotos.length >= 4) {
                        heroContainer.style.display = 'grid';
                        heroContainer.style.gridTemplateColumns = '1fr 1fr';
                        heroContainer.style.gridTemplateRows = '1fr 1fr';
                        heroContainer.style.gap = '8px';
                        mPhotos.slice(0, 4).forEach(p => {
                            heroContainer.innerHTML += `<img src="/api/photo/file/${encodeURIComponent(p)}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />`;
                        });
                    }
                }"""

if old_js in js_code:
    js_code = js_code.replace(old_js, new_js)
else:
    print("Warning: could not find heroImg replace block")


# Replace preloader URLs logic so it uses moment_photos instead of memorable_moment
old_preload = """if (data.memorable_moment) preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.memorable_moment)}`);"""
new_preload = """if (data.moment_photos) {
                    preloadUrls = preloadUrls.concat(data.moment_photos.map(p => `/api/photo/file/${encodeURIComponent(p)}`));
                } else if (data.memorable_moment) {
                    preloadUrls.push(`/api/photo/file/${encodeURIComponent(data.memorable_moment)}`);
                }"""

if old_preload in js_code:
    js_code = js_code.replace(old_preload, new_preload)


# Replace playSkiper79Transition arguments to pass moment_photos
old_transition_next = """if (nextSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.memorable_moment ? [recapData.memorable_moment] : null; }"""
new_transition_next = """if (nextSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.moment_photos && recapData.moment_photos.length > 0 ? recapData.moment_photos : (recapData?.memorable_moment ? [recapData.memorable_moment] : null); }"""

old_transition_prev = """if (prevSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.memorable_moment ? [recapData.memorable_moment] : null; }"""
new_transition_prev = """if (prevSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.moment_photos && recapData.moment_photos.length > 0 ? recapData.moment_photos : (recapData?.memorable_moment ? [recapData.memorable_moment] : null); }"""


if old_transition_next in js_code:
    js_code = js_code.replace(old_transition_next, new_transition_next)
if old_transition_prev in js_code:
    js_code = js_code.replace(old_transition_prev, new_transition_prev)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("JS patched!")
