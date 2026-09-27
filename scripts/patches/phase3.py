import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Implement playSkiper79Transition
skiper79_func = '''
function playSkiper79Transition(titleText, callback) {
    if (isRecapTransitioning) return;
    isRecapTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'flex';
    layer.style.alignItems = 'center';
    layer.style.justifyContent = 'center';
    layer.style.overflow = 'hidden';
    layer.innerHTML = '';
    
    // Skiper 79 aesthetic: Dark glass background, massive typography sweeping across
    layer.style.background = 'rgba(0,0,0,0.85)';
    layer.style.backdropFilter = 'blur(20px)';
    layer.style.opacity = '0';
    
    // Create massive text container
    const textContainer = document.createElement('div');
    textContainer.style.position = 'relative';
    textContainer.style.width = '100vw';
    textContainer.style.height = '100vh';
    textContainer.style.display = 'flex';
    textContainer.style.alignItems = 'center';
    textContainer.style.justifyContent = 'center';
    textContainer.style.overflow = 'hidden';
    
    const h1 = document.createElement('h1');
    h1.innerText = titleText;
    h1.style.fontFamily = "'Outfit', sans-serif";
    h1.style.fontWeight = '900';
    h1.style.fontSize = '12vw';
    h1.style.color = 'transparent';
    h1.style.WebkitTextStroke = '2px rgba(255,255,255,0.8)';
    h1.style.whiteSpace = 'nowrap';
    h1.style.textTransform = 'uppercase';
    h1.style.transform = 'translateX(100vw)'; // Start offscreen right
    
    textContainer.appendChild(h1);
    layer.appendChild(textContainer);
    
    // Fade in overlay
    gsap.to(layer, { opacity: 1, duration: 0.4, ease: "power2.out" });
    
    // Sweep text across
    gsap.to(h1, {
        x: '-100vw',
        duration: 2.5,
        ease: "power2.inOut",
        onUpdate: function() {
            // Swap slide exactly when text is crossing the center
            if (this.progress() > 0.45 && this.progress() < 0.55 && callback) {
                callback();
                callback = null; // Ensure it only runs once
            }
        },
        onComplete: () => {
            gsap.to(layer, {
                opacity: 0,
                duration: 0.4,
                ease: "power2.in",
                onComplete: () => {
                    layer.style.display = 'none';
                    isRecapTransitioning = false;
                }
            });
        }
    });
}
'''

# We need to inject this function before playSlideTransition
js_code = js_code.replace("// --- [REGION: SLIDE TRANSITION LOGIC] ---", "// --- [REGION: SLIDE TRANSITION LOGIC] ---\n" + skiper79_func)

# Now, we need to modify nextRecapSlide and prevRecapSlide to occasionally use playSkiper79Transition
# For example, transitioning into the "Person" or "Place" slides could trigger it.
# Wait, a safer way is to just inject it into playSlideTransition as a random option, or when transitioning to specific slides.
# Let's modify nextRecapSlide so that if the next slide is 'slide-person', it plays Skiper 79 "TOP PERSON", etc.

old_next = '''function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        playSlideTransition(() => {
            recapCurrentSlide++;
            showRecapSlide(recapCurrentSlide);
        });
    } else {
        closeRecapPlayer();
    }
}'''

new_next = '''function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        let nextSlideId = recapSlides[recapCurrentSlide + 1].id;
        
        let transitionTitle = null;
        if (nextSlideId === 'slide-person') transitionTitle = "TOP PERSON";
        if (nextSlideId === 'slide-place') transitionTitle = "ICONIC PLACE";
        if (nextSlideId === 'slide-hero') transitionTitle = "HERO MOMENT";
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });
        } else {
            playSlideTransition(() => {
                recapCurrentSlide++;
                showRecapSlide(recapCurrentSlide);
            });
        }
    } else {
        closeRecapPlayer();
    }
}'''

js_code = js_code.replace(old_next, new_next)

# And similarly for prevRecapSlide (though going backward maybe standard transition is fine, but let's do it too for consistency)
old_prev = '''function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        playSlideTransition(() => {
            recapCurrentSlide--;
            showRecapSlide(recapCurrentSlide);
        });
    }
}'''

new_prev = '''function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        let prevSlideId = recapSlides[recapCurrentSlide - 1].id;
        
        let transitionTitle = null;
        if (prevSlideId === 'slide-person') transitionTitle = "TOP PERSON";
        if (prevSlideId === 'slide-place') transitionTitle = "ICONIC PLACE";
        if (prevSlideId === 'slide-hero') transitionTitle = "HERO MOMENT";
        
        if (transitionTitle) {
            playSkiper79Transition(transitionTitle, () => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
        } else {
            playSlideTransition(() => {
                recapCurrentSlide--;
                showRecapSlide(recapCurrentSlide);
            });
        }
    }
}'''

js_code = js_code.replace(old_prev, new_prev)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
    
print("Injected Skiper 79 Phase 3 logic")
