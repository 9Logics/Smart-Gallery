import re

# 1. Update JS to use coverflowEffect for Skiper 54
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

old_swiper = """    new Swiper('.skiper-54-swiper', {
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
    });"""

new_swiper = """    new Swiper('.skiper-54-swiper', {
        effect: 'coverflow',
        slidesPerView: 'auto',
        centeredSlides: true,
        grabCursor: true,
        loop: true,
        observer: true,
        observeParents: true,
        coverflowEffect: {
            rotate: 0,
            stretch: -50, /* negative stretch overlaps them */
            depth: 300, /* pushes them back, scaling them down natively */
            modifier: 1,
            slideShadows: true,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });"""

js_code = js_code.replace(old_swiper, new_swiper)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)


# 2. Update CSS to remove overriding transforms that break Swiper's 3D layout
css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

css_code = re.sub(r"transform:\s*scale\(0\.7\)\s*!important;", "", css_code)
css_code = re.sub(r"transform:\s*scale\(1\.05\)\s*!important;", "", css_code)
css_code = re.sub(r"transition:\s*transform[^;]+;", "transition: opacity 0.5s ease !important;", css_code)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_code)

print("Applied coverflow effect and cleaned CSS transforms!")
