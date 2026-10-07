import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove from old location
target_remove = """                    <!-- Bottom Grid Arrow Inside the Card -->
                    <button id="story-grid-btn" class="story-grid-bottom-btn"><i data-lucide="chevron-down"></i></button>"""
html = html.replace(target_remove, "")

# Add to new location (after story-next-card)
target_insert = """            <div id="story-next-card" class="story-preview-card next hidden">
                <div class="preview-overlay"></div>
                <div class="preview-text-container">
                    <span class="preview-label">Up next</span>
                    <span id="story-next-title" class="preview-title"></span>
                </div>
            </div>"""

replacement_insert = """            <div id="story-next-card" class="story-preview-card next hidden">
                <div class="preview-overlay"></div>
                <div class="preview-text-container">
                    <span class="preview-label">Up next</span>
                    <span id="story-next-title" class="preview-title"></span>
                </div>
            </div>
            
            <!-- Bottom Grid Arrow (Moved from card to screen) -->
            <button id="story-grid-btn" class="story-grid-bottom-btn"><i data-lucide="chevron-down"></i></button>"""

if target_insert in html:
    html = html.replace(target_insert, replacement_insert)
    print("HTML updated!")
else:
    print("HTML target not found!")

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
