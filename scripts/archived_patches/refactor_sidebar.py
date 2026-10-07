import re

with open('app/templates/partials/lightbox-modal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the old sidebar HTML with a fixed header structure
old_sidebar_start = html.find('<aside class="lightbox-sidebar" id="lightbox-sidebar">')
old_sidebar_end = html.find('</aside>', old_sidebar_start) + 8

old_sidebar = html[old_sidebar_start:old_sidebar_end]

# We want to replace the first two divs inside <aside> with our new header and scroll area
# Actually, the entire inside of the aside needs to be adjusted.
# Let's rebuild the inside of the sidebar using string replacement or regex.

header_pattern = r'<div style="display:flex; justify-content:space-between; align-items:center; padding: 16px 20px 0 20px;">\s*<h2 style="margin:0; font-size:24px; font-weight: 700; letter-spacing: -0.5px;">Info</h2>\s*<button id="close-info-panel-btn".*?</button>\s*</div>'

header_match = re.search(header_pattern, old_sidebar, re.DOTALL)
if header_match:
    # We will replace the header match with a sticky header.
    # The external buttons are top: 24px, height: 44px. So they occupy Y=24 to Y=68.
    # The sidebar is at top: 24px. So its internal Y=0 maps to screen Y=24.
    # To align exactly, the header should have height 44px and no top margin!
    new_header = """
    <div class="sidebar-header" style="position: sticky; top: 0; z-index: 10; display:flex; justify-content:space-between; align-items:center; height: 44px; padding: 0 24px; background: inherit; border-bottom: 1px solid rgba(255,255,255,0.05); flex-shrink: 0;">
        <h2 style="margin:0; font-size:20px; font-weight: 700; letter-spacing: -0.5px;">Info</h2>
        <button id="close-info-panel-btn" class="btn-icon" style="background:rgba(255,255,255,0.08); padding:0; border-radius: 50%; transition: background 0.2s; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center;" onmouseover="this.style.background='rgba(255,255,255,0.15)'" onmouseout="this.style.background='rgba(255,255,255,0.08)'"><i data-lucide="x" style="width:16px; height:16px; color: #fff;"></i></button>
    </div>
    <div class="sidebar-scroll-area" style="overflow-y: auto; flex-grow: 1; padding: 20px 24px 32px 24px; display: flex; flex-direction: column; gap: 4px;">
    """
    
    # We also need to close the sidebar-scroll-area div at the end of the aside
    modified_sidebar = old_sidebar[:header_match.start()] + new_header + old_sidebar[header_match.end():]
    
    # The original <div class="sidebar-section" style="..."> was right after the header.
    # Let's remove its inline padding-top and padding-bottom since we moved it to the scroll area.
    modified_sidebar = modified_sidebar.replace('style="padding-top: 12px; display: flex; flex-direction: column; gap: 4px; padding-bottom: 16px;"', 'style="display: flex; flex-direction: column; gap: 4px;"')
    
    # Add closing div for sidebar-scroll-area before </aside>
    modified_sidebar = modified_sidebar.replace('</aside>', '</div>\n        </aside>')
    
    html = html[:old_sidebar_start] + modified_sidebar + html[old_sidebar_end:]
    
    with open('app/templates/partials/lightbox-modal.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully patched sidebar HTML")
else:
    print("Header pattern not found!")
