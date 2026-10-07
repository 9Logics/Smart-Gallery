import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

old_block = r"""function createCyclingDeck(containerId, photos, featurePhoto) {
    // [PHASE 2 PLACEHOLDER]
    // This will be replaced by Skiper 47 & 54 logic
    const container = document.getElementById(containerId);
    if (container) container.innerHTML = '';
}"""

new_block = '''function initSkiper47Carousel(containerId, photos, featurePhoto) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    let deck = [];
    if (featurePhoto) deck.push(featurePhoto);
    for (let i = 0; i < photos.length; i++) {
        if (deck.length >= 10) break;
        if (photos[i] !== featurePhoto && !deck.includes(photos[i])) deck.push(photos[i]);
    }
    
    let swiperHtml = `<div class="swiper skiper-47-swiper"><div class="swiper-wrapper">`;
    deck.forEach(p => {
        swiperHtml += `<div class="swiper-slide skiper-47-slide"><img src="/api/photo/file/${encodeURIComponent(p)}" /></div>`;
    });
    swiperHtml += `</div><div class="swiper-pagination"></div></div>`;
    
    container.innerHTML = swiperHtml;
    
    new Swiper('.skiper-47-swiper', {
        effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto',
        coverflowEffect: {
            rotate: 20,
            stretch: 0,
            depth: 250,
            modifier: 1,
            slideShadows: true,
        },
        pagination: { el: '.swiper-pagination', clickable: true },
        autoplay: { delay: 3000, disableOnInteraction: false }
    });
}

function initSkiper54Carousel(containerId, photos) {
    const container = document.getElementById(containerId);
    if (!container || !photos || photos.length === 0) return;
    
    container.style.position = 'relative';
    container.style.width = '70vw';
    container.style.height = '60vh';
    container.style.margin = '0 auto';
    container.style.overflow = 'hidden';
    container.style.borderRadius = '24px';
    container.style.boxShadow = '0 30px 60px rgba(0,0,0,0.6)';
    
    let deck = photos.slice(0, 7);
    let html = '';
    deck.forEach((p, i) => {
        let isFirst = i === 0;
        html += `<img src="/api/photo/file/${encodeURIComponent(p)}" class="skiper-54-img" style="position: absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; z-index:${10 - i}; clip-path: inset(0 ${isFirst ? '0%' : '100%'} 0 0);" />`;
    });
    container.innerHTML = html;
    
    let imgs = container.querySelectorAll('.skiper-54-img');
    if (imgs.length <= 1) return;
    
    let currentIndex = 0;
    let cycle = setInterval(() => {
        let currentImg = imgs[currentIndex];
        let nextIndex = (currentIndex + 1) % imgs.length;
        let nextImg = imgs[nextIndex];
        
        nextImg.style.zIndex = 20;
        currentImg.style.zIndex = 10;
        nextImg.style.clipPath = 'inset(0 0 0 100%)';
        
        gsap.to(nextImg, {
            clipPath: 'inset(0 0% 0 0%)',
            duration: 1.4,
            ease: "power3.inOut"
        });
        
        gsap.to(currentImg, {
            scale: 0.85,
            opacity: 0.4,
            duration: 1.4,
            ease: "power3.inOut",
            onComplete: () => {
                currentImg.style.zIndex = 1;
                currentImg.style.scale = 1;
                currentImg.style.opacity = 1;
            }
        });
        
        currentIndex = nextIndex;
    }, 3500);
    
    window.recapDeckIntervals = window.recapDeckIntervals || [];
    window.recapDeckIntervals.push(cycle);
}'''

js_code = js_code.replace(old_block, new_block)

# Replace the calls
js_code = js_code.replace("createCyclingDeck('person-photos-fan', data.top_person_photos, data.top_person_feature);", "initSkiper47Carousel('person-photos-fan', data.top_person_photos, data.top_person_feature);")
js_code = js_code.replace("createCyclingDeck('place-photos-fan', data.iconic_place_photos, null);", "initSkiper54Carousel('place-photos-fan', data.iconic_place_photos);")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
    
print("Successfully injected new JS for Phase 2")
