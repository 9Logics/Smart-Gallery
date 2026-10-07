import re

# 1. Extract recap_dashboard script from index.html
html_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

# Find the specific script block
script_pattern = r"\s*<script>\s*// Fetch dynamic years and setup recap UI.*?\}\);\s*</script>"
match = re.search(script_pattern, html_code, flags=re.DOTALL)

if match:
    script_content = match.group(0)
    # Extract just the JS code without <script> tags
    js_content = re.sub(r"^\s*<script>\s*", "", script_content)
    js_content = re.sub(r"\s*</script>$", "", js_content)
    
    # Add helpful region markers for future agents
    js_content = "// --- [REGION: DASHBOARD INIT] ---\n" + js_content + "\n// --- [END REGION: DASHBOARD INIT] ---\n"
    
    # Write to new file
    with open(r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_dashboard.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    # Replace in index.html with a file reference
    new_script_tag = '\n    <!-- Modularized Dashboard Logic -->\n    <script src="/static/js/recap_dashboard.js?v=316"></script>'
    html_code = html_code.replace(script_content, new_script_tag)
    html_code = html_code.replace("v=315", "v=316")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    print("Extracted recap dashboard logic into recap_dashboard.js")
else:
    print("Could not find the script block in index.html")


# 2. Add structural markers to recap_player.js
js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

if "// --- [REGION: STATE VARIABLES] ---" not in js_code:
    js_code = js_code.replace("let isRecapLoading", "// --- [REGION: STATE VARIABLES] ---\nlet isRecapLoading")
    
    js_code = js_code.replace("function openRecapPlayer(", "\n// --- [REGION: OPEN & INIT PLAYER] ---\nfunction openRecapPlayer(")
    
    js_code = js_code.replace("function closeRecapPlayer(", "\n// --- [REGION: CLOSE PLAYER] ---\nfunction closeRecapPlayer(")
    
    js_code = js_code.replace("function playSlideTransition(", "\n// --- [REGION: SLIDE TRANSITION LOGIC] ---\nfunction playSlideTransition(")
    
    js_code = js_code.replace("function createCyclingDeck(", "\n// --- [REGION: CYCLING DECK ENGINE (SKIPER-54)] ---\nfunction createCyclingDeck(")
    
    js_code = js_code.replace("function handleParallaxMouseMove(", "\n// --- [REGION: PARALLAX & MOUSE DEPTH (SIENA/SKIPER-29)] ---\nfunction handleParallaxMouseMove(")
    
    js_code = js_code.replace("function handleRecapKeyboard(", "\n// --- [REGION: EVENT HANDLERS] ---\nfunction handleRecapKeyboard(")

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print("Added structural region markers to recap_player.js")

