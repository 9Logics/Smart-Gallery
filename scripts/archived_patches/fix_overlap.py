import re

html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

old_person = '''<div class="recap-slide siena-depth" id="slide-person">
                <h2 class="siena-layer" data-depth="20">You spent the most time with</h2>
                <div id="person-photos-fan" class="siena-layer" data-depth="50"></div>
                <h1 class="siena-layer" data-depth="70" id="recap-stat-person"></h1>
            </div>'''

new_person = '''<div class="recap-slide siena-depth" id="slide-person" style="display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 2vh;">
                <h2 class="siena-layer" data-depth="20" style="position: relative !important; margin: 0 !important; font-size: 5vh !important; line-height: 1 !important; z-index: 100;">YOU SPENT THE MOST TIME WITH</h2>
                <div id="person-photos-fan" class="siena-layer" data-depth="50" style="position: relative !important; width: 100vw; height: 50vh; display: flex; justify-content: center; align-items: center; margin: 0 !important; z-index: 50;"></div>
                <h1 class="siena-layer" data-depth="70" id="recap-stat-person" style="position: relative !important; margin: 0 !important; font-size: 6vh !important; line-height: 1 !important; z-index: 100;"></h1>
            </div>'''

old_place = '''<div class="recap-slide siena-depth" id="slide-place">
                <h2 class="siena-layer" data-depth="20">You explored</h2>
                <div id="place-photos-fan" class="siena-layer" data-depth="50"></div>
                <h1 class="siena-layer" data-depth="70" id="recap-stat-place"></h1>
            </div>'''

new_place = '''<div class="recap-slide siena-depth" id="slide-place" style="display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 2vh;">
                <h2 class="siena-layer" data-depth="20" style="position: relative !important; margin: 0 !important; font-size: 5vh !important; line-height: 1 !important; z-index: 100;">YOU EXPLORED</h2>
                <div id="place-photos-fan" class="siena-layer" data-depth="50" style="position: relative !important; width: 100vw; height: 50vh; display: flex; justify-content: center; align-items: center; margin: 0 !important; z-index: 50;"></div>
                <h1 class="siena-layer" data-depth="70" id="recap-stat-place" style="position: relative !important; margin: 0 !important; font-size: 6vh !important; line-height: 1 !important; z-index: 100;"></h1>
            </div>'''

html_code = html_code.replace(old_person, new_person)
html_code = html_code.replace(old_place, new_place)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print("Injected foolproof flex gap layouts to index.html")
