import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = """                          <button id="story-mute-btn" class="btn-icon story-bottom-btn hidden"><i data-lucide="volume-2"></i></button>
                      </div>
                          <button id="story-mute-btn" class="btn-icon story-bottom-btn"><i data-lucide="volume-2"></i></button>
                      </div>"""

replacement = """                          <button id="story-mute-btn" class="btn-icon story-bottom-btn hidden"><i data-lucide="volume-2"></i></button>
                      </div>"""

if target in html:
    html = html.replace(target, replacement)
    print("Fixed broken HTML divs!")
else:
    print("Target not found!")

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
