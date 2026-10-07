import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

old_block = r'''            setTimeout\(\(\) => \{
                // Slide up preloader \(Skiper 15\)
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

new_block = '''            setTimeout(() => {
                // PRELOADER: Wait for all high-res main images to download
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
                
                let preloaderText = document.querySelector('.preloader-text');
                if(preloaderText) preloaderText.innerText = "Developing high-res photos...";
                
                Promise.all(loadPromises).then(() => {
                    // Slide up preloader (Skiper 15)
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
            }, 100);'''

js_code = re.sub(old_block, new_block, js_code, flags=re.DOTALL)
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print("Injected Promise.all")
