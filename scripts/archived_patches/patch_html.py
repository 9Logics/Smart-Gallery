import re
path = 'app/templates/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

target = """<div class="rewind-dashboard" id="rewind-dashboard">
            <!-- Hero: Current Year Recap -->"""

replacement = """<div class="rewind-dashboard" id="rewind-dashboard">
            <div id="beta-marker" style="position: absolute; top: -10px; right: 20px; background: #FF3B30; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 800; font-size: 14px; letter-spacing: 1px; z-index: 100; box-shadow: 0 4px 12px rgba(255, 59, 48, 0.4); text-transform: uppercase;">BETA</div>
            <!-- Hero: Current Year Recap -->"""

if "id=\"beta-marker\"" not in html:
    html = html.replace(target, replacement)
    # bump cache
    html = html.replace("v=398", "v=399")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added BETA marker")
else:
    print("BETA marker already exists")
