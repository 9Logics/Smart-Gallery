import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

start_idx = js_code.find("function initSkiper54Carousel(containerId, photos) {")
end_idx = js_code.find("currentIndex = nextIndex;\n    }, 4000);", start_idx) + 40 # approximate
# Let's find exactly where it ends:
end_idx = js_code.find("window.recapDeckIntervals.push(cycle);", start_idx)
if end_idx != -1:
    end_idx = js_code.find("}", end_idx) + 1

new_fn = '''function initSkiper54Carousel(containerId, photos) {
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
        slidesPerView: 'auto',
        centeredSlides: true,
        spaceBetween: 40,
        grabCursor: true,
        loop: true,
        observer: true,
        observeParents: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
}'''

js_code = js_code[:start_idx] + new_fn + js_code[end_idx:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Rewrote initSkiper54Carousel to use SwiperJS")
