import re

css_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_code = f.read()

# 1. Remove the Phase F typography chunky shadows
css_code = re.sub(r"#recap-stat-person,\s*#recap-stat-place,\s*\.number-flow-wrapper\s*\{[^}]+\}", "", css_code)
css_code = re.sub(r"#recap-stat-person\s*\{[^}]+\}", "", css_code) # the transform rotate

# 2. Remove Polaroid styles
css_code = re.sub(r"\.(person|place)-fan-photo(\.feature-photo)?\s*\{[^}]+\}", "", css_code)
css_code = re.sub(r"\.(person|place)-fan-photo img\s*\{[^}]+\}", "", css_code)

# 3. Remove Montage Burst styles
css_code = re.sub(r"\.montage-burst-photo\s*\{[^}]+\}", "", css_code)
css_code = re.sub(r"\.montage-burst-photo img\s*\{[^}]+\}", "", css_code)
css_code = re.sub(r"#montage-container\s*\{[^}]+\}", "", css_code)

# 4. Strip the background color overrides from the stats text to make it cleaner
css_code = re.sub(r"#recap-stat-person,\s*#recap-stat-place\s*\{[^}]+\}", 
r"""#recap-stat-person, #recap-stat-place {
    font-family: 'Outfit', sans-serif;
    font-size: 3rem !important;
    font-weight: 800;
    color: #fff;
    padding: 10px 40px;
    border-radius: 8px;
    letter-spacing: -1px;
}""", css_code)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_code)
    
print("Purged old polaroid and chunky scrapbook styles from CSS")
