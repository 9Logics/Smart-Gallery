import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add the window AI gradient inside the pixel-preloader
old_html = '''        <!-- Skiper11: Pixel Preloader -->
        <div class="pixel-preloader" id="pixel-preloader">
            <div class="pixel-counter" id="pixel-counter">0%</div>
            <div class="pixel-grid" id="pixel-grid"></div>
        </div>'''

new_html = '''        <!-- Skiper11: Pixel Preloader -->
        <div class="pixel-preloader" id="pixel-preloader">
            <div class="window-ai-gradient"></div>
            <div class="pixel-counter" id="pixel-counter">0%</div>
            <div class="pixel-grid" id="pixel-grid"></div>
        </div>'''

if old_html in html:
    html = html.replace(old_html, new_html)
    html = html.replace('v=252', 'v=253') # We reverted, so maybe it's back to 251. Let's just blindly replace 251 to 253
    html = html.replace('v=251', 'v=253')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added HTML window AI gradient!")
else:
    print("Could not find HTML block!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Add the CSS for window AI gradient
ai_css = '''
/* Apple Intelligence Window Edge Gradient (Skiper86) */
.window-ai-gradient {
    position: absolute;
    inset: 0;
    z-index: 15; /* Above everything in the preloader */
    pointer-events: none;
    padding: 6px; /* Edge thickness */
    overflow: hidden;
    /* CSS Mask to cut out the center and only show the padded edge */
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    /* Inner glow shadow */
    box-shadow: inset 0 0 30px rgba(161, 140, 209, 0.5);
}

.window-ai-gradient::before {
    content: '';
    position: absolute;
    inset: -100%;
    /* Apple Intelligence colors */
    background: conic-gradient(from 0deg at 50% 50%, #4facfe, #00f2fe, #a18cd1, #fbc2eb, #4facfe);
    animation: ai-window-spin 5s linear infinite;
}

@keyframes ai-window-spin {
    100% { transform: rotate(360deg); }
}
'''
if '.window-ai-gradient' not in css:
    css += ai_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added CSS window AI gradient!")
