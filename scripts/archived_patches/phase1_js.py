import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# 1. Nullify createCyclingDeck
old_cycling = r"function createCyclingDeck\(containerId, photos, featurePhoto\) \{[\s\S]*?\}\s*\}\s*\}\);\s*\}\s*\}"
new_cycling = r"function createCyclingDeck(containerId, photos, featurePhoto) {\n    // [PHASE 2 PLACEHOLDER]\n    // This will be replaced by Skiper 47 & 54 logic\n    const container = document.getElementById(containerId);\n    if (container) container.innerHTML = '';\n}"
js_code = re.sub(old_cycling, new_cycling, js_code)

# 2. Nullify Montage Burst Injection in openRecapPlayer
# We want to find: `// Populate Montage Burst (Slide 0) ...` up to the preloader definition, wait! The preloader definition is earlier, but we injected the Promise.all logic!
# Oh wait, we injected Promise.all inside `setTimeout(() => {`.
# The montage burst logic is right before the Promise.all logic.

js_code = re.sub(
    r"// Populate Montage Burst \(Slide 0\)[\s\S]*?(?=// PRELOADER: Wait for all high-res main images)", 
    r"// [PHASE 1] Montage Burst removed (Slide 0 will be skipped or replaced by Skiper 79)\n            ", 
    js_code
)

# Wait, if we remove Montage Burst, what happens to `recapCurrentSlide = 0; showRecapSlide(0);` ? 
# Slide 0 currently is `#slide-montage`. If it's empty, it will just show nothing.
# We should probably hide `#slide-montage` permanently.
js_code = js_code.replace("recapCurrentSlide = 0;\n", "recapCurrentSlide = 0; document.getElementById('slide-montage').style.display = 'none';\n")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Purged old js logic.")
