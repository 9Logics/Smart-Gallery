import re

with open('app/static/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target_content = """.story-grid-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
}
.story-grid-item {
    aspect-ratio: 1;
    border-radius: 8px;
    background-size: cover;
    background-position: center;
    cursor: pointer;
    transition: transform 0.2s;
}"""

replacement_content = """.story-grid-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-content: flex-start;
}
.story-grid-item {
    height: 160px;
    width: auto;
    border-radius: 8px;
    object-fit: cover;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}"""

if target_content in css:
    css = css.replace(target_content, replacement_content)
    print("Replaced grid content CSS")
else:
    print("Grid content CSS not found!")

# Also fix the z-index so lightbox is on top of story viewer
target_zindex = """.story-lightbox {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    z-index: 9999;"""

replacement_zindex = """.story-lightbox {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    z-index: 400; /* Lower than lightbox (500) so lightbox opens ON TOP */"""

if target_zindex in css:
    css = css.replace(target_zindex, replacement_zindex)
    print("Replaced zindex")
else:
    print("zindex CSS not found!")

with open('app/static/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
