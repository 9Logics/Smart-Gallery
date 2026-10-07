js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update navigation transitions (nextRecapSlide)
t1 = '''        if (nextSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }
        if (nextSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.moment_photos && recapData.moment_photos.length > 0 ? recapData.moment_photos : (recapData?.memorable_moment ? [recapData.memorable_moment] : null); }'''
r1 = '''        if (nextSlideId === 'slide-top-places') { transitionTitle = "EPIC JOURNEYS"; transitionPhotos = recapData?.top_places?.[0]?.photos || null; }'''
js = js.replace(t1, r1)

# 1b. Update navigation transitions (prevRecapSlide)
t2 = '''        if (prevSlideId === 'slide-place') { transitionTitle = "ICONIC PLACE"; transitionPhotos = recapData?.iconic_place_photos || null; }
        if (prevSlideId === 'slide-hero') { transitionTitle = "HERO MOMENT"; transitionPhotos = recapData?.moment_photos && recapData.moment_photos.length > 0 ? recapData.moment_photos : (recapData?.memorable_moment ? [recapData.memorable_moment] : null); }'''
r2 = '''        if (prevSlideId === 'slide-top-places') { transitionTitle = "EPIC JOURNEYS"; transitionPhotos = recapData?.top_places?.[0]?.photos || null; }'''
js = js.replace(t2, r2)

# 2. Add Accordion Builder and Sequence player
accordion_logic = '''
// --- [REGION: TOP PLACES ACCORDION] ---
function buildPlacesAccordion(places) {
    const accordion = document.getElementById('places-accordion');
    if (!accordion) return;
    accordion.innerHTML = '';
    
    if (!places || places.length === 0) {
        document.getElementById('slide-top-places').style.display = 'none';
        return;
    }
    
    places.forEach((place, i) => {
        const item = document.createElement('div');
        item.className = 'place-accordion-item';
        item.id = `place-item-${i}`;
        
        // Thumbnail for collapsed state
        if (place.photos && place.photos.length > 0) {
            item.style.backgroundImage = `url('/api/photo/thumbnail/${encodeURIComponent(place.photos[0])}')`;
            item.style.backgroundSize = 'cover';
            item.style.backgroundPosition = 'center';
        }
        
        const title = document.createElement('div');
        title.className = 'place-item-title';
        title.innerText = place.name;
        item.appendChild(title);
        
        const wrapper = document.createElement('div');
        wrapper.className = 'place-carousel-wrapper';
        
        let swiperHtml = `<div class="swiper place-swiper-${i}"><div class="swiper-wrapper">`;
        place.photos.slice(0, 15).forEach(p => {
            swiperHtml += `<div class="swiper-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" /></div>`;
        });
        swiperHtml += `</div></div>`;
        wrapper.innerHTML = swiperHtml;
        item.appendChild(wrapper);
        
        item.addEventListener('click', () => {
            if (window.placeAutoAnim) {
                window.placeAutoAnim.kill();
                window.placeAutoAnim = null;
            }
            document.querySelectorAll('.place-accordion-item').forEach(el => el.classList.remove('expanded'));
            item.classList.add('expanded');
        });
        
        accordion.appendChild(item);
        
        new Swiper(`.place-swiper-${i}`, {
            loop: true,
            effect: 'fade',
            fadeEffect: { crossFade: true },
            autoplay: { delay: 1500, disableOnInteraction: false },
            allowTouchMove: false
        });
    });
}

function playPlacesAccordionSequence() {
    const items = document.querySelectorAll('.place-accordion-item');
    if (!items || items.length === 0) return;
    
    if (window.placeAutoAnim) window.placeAutoAnim.kill();
    items.forEach(el => el.classList.remove('expanded'));
    
    const tl = gsap.timeline();
    window.placeAutoAnim = tl;
    
    // Animate each one popping open for 3 seconds
    items.forEach((item, i) => {
        tl.call(() => {
            items.forEach(el => el.classList.remove('expanded'));
            item.classList.add('expanded');
        });
        tl.to({}, { duration: 3.5 }); 
    });
    
    // Finally, collapse all and wait for user interaction
    tl.call(() => {
        items.forEach(el => el.classList.remove('expanded'));
    });
}
'''

js = js.replace('// --- [REGION: CLOSE PLAYER] ---', accordion_logic + '\n// --- [REGION: CLOSE PLAYER] ---')

# 3. Modify openRecapPlayer to call buildPlacesAccordion and remove old place/hero init
t3 = '''            if (data.iconic_place) {
                document.getElementById('recap-stat-place').innerText = data.iconic_place;
                
                initSkiper54Carousel('place-photos-fan', data.iconic_place_photos);
            } else {
                document.getElementById('slide-place').style.display = 'none'; // skip
            }
            
            // Hero
            if (!data.moment_photos || data.moment_photos.length === 0) {
                if (!data.memorable_moment) {
                    document.getElementById('slide-hero').style.display = 'none';
                }
            }'''
r3 = '''            if (data.top_places && data.top_places.length > 0) {
                buildPlacesAccordion(data.top_places);
            } else {
                document.getElementById('slide-top-places').style.display = 'none';
            }'''
js = js.replace(t3, r3)

# 4. Modify showRecapSlide to trigger playPlacesAccordionSequence
t4 = '''            // Montage Transition Buffer Slide
            if (s.id === 'slide-montage' && recapData) {'''
r4 = '''            // Epic Journeys Auto-Sequence
            if (s.id === 'slide-top-places') {
                playPlacesAccordionSequence();
            }

            // Montage Transition Buffer Slide
            if (s.id === 'slide-montage' && recapData) {'''
js = js.replace(t4, r4)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched recap_player.js for Epic Journeys accordion")
