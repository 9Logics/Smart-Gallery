import re
path = 'app/static/js/selection.js'
with open(path, 'r', encoding='utf-8') as f:
    js = f.read()

target = """// Scan Faces for Selected Photos
if (elements.multiScanBtn) {
    elements.multiScanBtn.addEventListener('click', async () => {"""

replacement = """// Scan Faces for Selected Photos
document.addEventListener('DOMContentLoaded', () => {
    if (elements.multiScanBtn) {
        elements.multiScanBtn.addEventListener('click', async () => {"""

js = js.replace(target, replacement)
js = js.replace("        }\n    });\n}", "        }\n    });\n    }\n});")

with open(path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Wrapped multiScanBtn logic in DOMContentLoaded")
