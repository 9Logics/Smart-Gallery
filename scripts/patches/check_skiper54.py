import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

start_idx = js_code.find("function initSkiper54Carousel(containerId, photos) {")
end_idx = js_code.find("function playSlideTransition(callback)", start_idx)
# wait, there's stuff between initSkiper54Carousel and playSlideTransition?
# Let's see what is after initSkiper54Carousel
