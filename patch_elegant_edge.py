import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_edge_css = '''/* Apple Intelligence Window Edge Gradient (Skiper86) */
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
}'''

new_edge_css = '''/* Elegant Window Edge Gradient (Theme Matched) */
.window-ai-gradient {
    position: absolute;
    inset: 0;
    z-index: 15;
    pointer-events: none;
    padding: 4px;
    overflow: hidden;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
}

.window-ai-gradient::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, #050505, var(--accent-color), #ffffff, var(--accent-color), #050505);
    background-size: 200% 200%;
    animation: edge-pulse 3s ease infinite;
}

@keyframes edge-pulse {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}'''

if old_edge_css in css:
    css = css.replace(old_edge_css, new_edge_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed CSS Edge Gradient!")
else:
    print("Could not find old edge css!")
