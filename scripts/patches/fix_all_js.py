import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# 1. Clean up nested initSkiper47Carousel
bad_pattern = re.compile(r"        function initSkiper47Carousel\(containerId, photos, featurePhoto\) \{.*?\n    \}\);?\n\}", re.DOTALL)
js_code = bad_pattern.sub("", js_code)

# 2. Patch the main initSkiper47Carousel to match Skiper 49
start_str = "new Swiper('.skiper-47-swiper', {"
end_str = "        });"
start_idx = js_code.find(start_str)

# Safely replace only the FIRST occurrence of Swiper init
if start_idx != -1:
    end_idx = js_code.find(end_str, start_idx) + len(end_str)
    
    new_swiper = """new Swiper('.skiper-47-swiper', {
        effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto',
        observer: true,
        observeParents: true,
        loop: true,
        coverflowEffect: {
            rotate: 45,
            stretch: -20,
            depth: 300,
            modifier: 1,
            slideShadows: true,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });"""
    
    js_code = js_code[:start_idx] + new_swiper + js_code[end_idx:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Applied Skiper 49 logic safely")
