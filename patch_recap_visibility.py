import os

js_path = 'app/static/js/core.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_logic = '''    // Toggle Zoom Widget Visibility
    const zoomContainer = document.getElementById('zoom-container');
    if (zoomContainer) {
        if (targetView === 'photos' || targetView === 'duplicates' || targetView === 'trash') {
            zoomContainer.style.display = 'flex';
        } else {
            zoomContainer.style.display = 'none';
        }
    }'''

new_logic = '''    // Toggle Zoom Widget Visibility
    const zoomContainer = document.getElementById('zoom-container');
    if (zoomContainer) {
        if (targetView === 'photos' || targetView === 'duplicates' || targetView === 'trash') {
            zoomContainer.style.display = 'flex';
        } else {
            zoomContainer.style.display = 'none';
        }
    }

    // Toggle Recap Trigger Visibility (only show on Home/Memories page)
    const recapTrigger = document.getElementById('recap-trigger');
    if (recapTrigger) {
        if (targetView === 'memories') {
            recapTrigger.style.display = 'flex';
        } else {
            recapTrigger.style.display = 'none';
        }
    }'''

if old_logic in js:
    js = js.replace(old_logic, new_logic)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched switchView to hide recap trigger!")
else:
    print("Could not find switchView zoom widget block!")

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('v=270', 'v=271')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
