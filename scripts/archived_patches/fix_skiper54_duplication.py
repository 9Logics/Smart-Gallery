import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Replace the deck extraction and Swiper config
old_block = """function initSkiper54Carousel(containerId, photos) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    let deck = photos.slice(0, 15);
    
    let swiperHtml = `<div class="swiper skiper-54-swiper"><div class="swiper-wrapper">`;
    deck.forEach(p => {
        swiperHtml += `<div class="swiper-slide skiper-54-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" class="skiper-54-img" /></div>`;
    });
    swiperHtml += `</div><div class="swiper-pagination"></div></div>`;
    
    container.innerHTML = swiperHtml;
    
    new Swiper('.skiper-54-swiper', {
        effect: 'coverflow',
        slidesPerView: 'auto',
        centeredSlides: true,
        grabCursor: true,
        loop: true,
        observer: true,
        observeParents: true,
        coverflowEffect: {
            rotate: 35,
            stretch: 0, /* negative stretch overlaps them */
            depth: 250, /* pushes them back, scaling them down natively */
            modifier: 1,
            slideShadows: true,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
}"""

new_block = """function initSkiper54Carousel(containerId, photos) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    // Ensure we have enough photos for the 3D loop effect to work properly.
    // If they only have 1 or 2 photos of this place, Swiper will look broken/empty.
    // We duplicate the array until we have at least 5 slides.
    let deck = [...photos];
    while (deck.length < 5) {
        deck = deck.concat(photos);
    }
    deck = deck.slice(0, 15);
    
    let swiperHtml = `<div class="swiper skiper-54-swiper"><div class="swiper-wrapper">`;
    deck.forEach(p => {
        swiperHtml += `<div class="swiper-slide skiper-54-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" class="skiper-54-img" /></div>`;
    });
    swiperHtml += `</div><div class="swiper-pagination"></div></div>`;
    
    container.innerHTML = swiperHtml;
    
    new Swiper('.skiper-54-swiper', {
        effect: 'coverflow',
        slidesPerView: 'auto',
        centeredSlides: true,
        grabCursor: true,
        loop: true,
        loopedSlides: deck.length, // Ensures cloning works right for auto width
        observer: true,
        observeParents: true,
        coverflowEffect: {
            rotate: 0,
            stretch: -40,
            depth: 250,
            modifier: 1,
            slideShadows: false, // Cleaner, modern flat look requested
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
}"""

if old_block in js_code:
    js_code = js_code.replace(old_block, new_block)
else:
    # Use regex if exact string mismatch
    start_idx = js_code.find("function initSkiper54Carousel(containerId, photos) {")
    end_idx = js_code.find("}\n\nfunction generateYearlyTheme(year) {")
    if end_idx == -1:
        end_idx = js_code.find("}\n\n// --- [REGION: CLOSE PLAYER] ---")
    if start_idx != -1 and end_idx != -1:
        js_code = js_code[:start_idx] + new_block + js_code[end_idx:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Updated initSkiper54Carousel with duplication logic and flat coverflow!")
