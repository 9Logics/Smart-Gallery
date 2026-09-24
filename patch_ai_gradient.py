import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Wrap the pixel-counter inside an AI gradient pill
old_counter = '<div class="pixel-counter" id="pixel-counter">0%</div>'
new_counter = '''<div class="ai-gradient-wrapper" id="pixel-counter-wrapper">
                <div class="ai-gradient-inner">
                    <div class="pixel-counter" id="pixel-counter">0%</div>
                </div>
            </div>'''

if old_counter in html:
    html = html.replace(old_counter, new_counter)

# Update the JS to fade out the WRAPPER instead of just the counter
old_js = 'counter.style.opacity = \'0\';'
new_js = "document.getElementById('pixel-counter-wrapper').classList.add('fade-out');"

if old_js in html:
    html = html.replace(old_js, new_js)

html = html.replace('v=251', 'v=252')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated HTML!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Update CSS for the counter
old_css = '''.pixel-counter {
    position: absolute;
    font-family: var(--font-mono, monospace);
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    z-index: 12;
    transition: opacity 0.2s ease;
}'''

new_css = '''/* Apple Intelligence Gradient Wrapper (Skiper86) */
.ai-gradient-wrapper {
    position: absolute;
    z-index: 13; /* Above the grid */
    padding: 2px;
    border-radius: 100px; /* Pill shape */
    overflow: hidden;
    transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 0 40px rgba(120, 0, 255, 0.3);
}

.ai-gradient-wrapper.fade-out {
    opacity: 0;
    transform: scale(1.2);
}

/* The spinning AI conic gradient */
.ai-gradient-wrapper::before {
    content: '';
    position: absolute;
    inset: -50%;
    /* Apple Intelligence / Siri gradient colors */
    background: conic-gradient(from 0deg, #4facfe, #00f2fe, #a18cd1, #fbc2eb, #4facfe);
    animation: ai-spin 3s linear infinite;
    z-index: 0;
}

@keyframes ai-spin {
    100% { transform: rotate(360deg); }
}

.ai-gradient-inner {
    position: relative;
    background: #050505;
    border-radius: 98px;
    padding: 12px 32px;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.pixel-counter {
    font-family: var(--font-mono, monospace);
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #fff;
    /* Apply a slight text gradient to match the border */
    background: linear-gradient(90deg, #fff, #e0e0e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}'''

if old_css in css:
    css = css.replace(old_css, new_css)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Updated CSS!")
