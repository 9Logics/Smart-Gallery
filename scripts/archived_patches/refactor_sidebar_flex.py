import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the header
header_start = html.find('<div class="sidebar-header"')
header_end = html.find('</div>', header_start) + 6

old_header = html[header_start:header_end]
new_header = """<div class="sidebar-header" style="display:flex; justify-content:space-between; align-items:center; height: 44px; padding: 0 24px; border-bottom: 1px solid rgba(255,255,255,0.08); flex-shrink: 0;">
        <h2 style="margin:0; font-size:18px; font-weight: 700; letter-spacing: -0.5px;">Info</h2>
        <button id="close-info-panel-btn" class="btn-icon" style="background:rgba(255,255,255,0.08); padding:0; border-radius: 50%; transition: background 0.2s; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center;" onmouseover="this.style.background='rgba(255,255,255,0.15)'" onmouseout="this.style.background='rgba(255,255,255,0.08)'"><i data-lucide="x" style="width:16px; height:16px; color: #fff;"></i></button>
    </div>"""

html = html.replace(old_header, new_header)

with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
    f.write(html)
