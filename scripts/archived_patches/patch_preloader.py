import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the preloader finish logic. Currently it's just:
# // Finish loader
# setTimeout(() => {
#    preloader.classList.add('slide-up');
#    ...
# }, 500); (or something similar)

# We want to intercept where it appends to gallery, personFan, placeFan, etc., collect all src URLs, and preload them.
# BUT we can just do a generic DOM check before hiding the preloader!
# Because the fetch block synchronously creates all the <img> tags in the DOM inside `#recap-player-overlay`!
# So at the END of the fetch block, we can find all `img` inside `#recap-player-overlay`, map them to Promises, and Promise.all them.

# Let's find the end of the fetch block.
old_finish_pattern = r"// Finish loader.*?setTimeout\(\(\) => \{.*?preloader\.classList\.add\('slide-up'\);.*?document\.getElementById\('recap-slides-container'\)\.classList\.remove\('hidden'\);.*?clone\.remove\(\);.*?element\.style\.opacity = '1';.*?recapCurrentSlide = 0;.*?playSlideTransition\(recapCurrentSlide\);.*?\}, 300\);"

new_finish = '''// Wait for all dynamically injected images to actually load over the network before hiding the preloader
            const overlayContainer = document.getElementById('recap-player-overlay');
            const imagesToLoad = Array.from(overlayContainer.querySelectorAll('img')).filter(img => !img.complete);
            
            const imagePromises = imagesToLoad.map(img => {
                return new Promise((resolve) => {
                    img.onload = resolve;
                    img.onerror = resolve; // Resolve even on error so we don't hang forever
                });
            });
            
            // Wait for both the images to load AND a minimum animation time for the 3D box (e.g. 1500ms total)
            const minPreloadTime = new Promise(resolve => setTimeout(resolve, 800));
            
            Promise.all([...imagePromises, minPreloadTime]).then(() => {
                // Slide up preloader (Skiper 15)
                preloader.classList.add('slide-up');
                
                // Show slides
                document.getElementById('recap-slides-container').classList.remove('hidden');
                
                // Remove clone
                clone.remove();
                element.style.opacity = '1';
                
                // Init sequence
                recapCurrentSlide = 0;
                playSlideTransition(recapCurrentSlide);
            });'''

js = re.sub(old_finish_pattern, new_finish, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched recap_player.js to preload images before starting.")
