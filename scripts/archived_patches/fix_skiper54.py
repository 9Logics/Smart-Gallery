import re

css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

css_code = re.sub(
    r"#person-photos-fan, #place-photos-fan\s*\{\s*height:\s*auto\s*!important;\s*\}",
    "#person-photos-fan, #place-photos-fan {\n    height: 50vh !important;\n}",
    css_code
)

# Also let's make sure Skiper 54 children don't overflow the 50vh.
# initSkiper54Carousel sets them to width:100%; height:100%; inline.
# I previously added:
# .skiper-54-img { position: static !important; ... }
# If they are position: static !important, they stack vertically instead of overlapping, breaking the clip-path wipe effect!
# Skiper 54 MUST have absolute positioning so the images stack on top of each other!
css_code = re.sub(
    r"\.skiper-54-img\s*\{\s*position:\s*static\s*!important;",
    ".skiper-54-img {\n    position: absolute !important;",
    css_code
)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_code)
print("Fixed Place container height and restored absolute positioning for Skiper 54")
