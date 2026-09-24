import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the instant display: none
old_js = '''                        setTimeout(() => {
                            preloader.style.display = 'none';
                            
                            // 1.5 seconds after reveal, morph to options'''
new_js = '''                        setTimeout(() => {
                            preloader.style.opacity = '0'; // Smooth fade out
                            setTimeout(() => {
                                preloader.style.display = 'none';
                            }, 800);
                            
                            // 1.5 seconds after reveal, morph to options'''
if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=261', 'v=262')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS fade out timing!")
else:
    print("Could not find JS display none block!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Add opacity transition to pixel preloader
old_preloader = '''.pixel-preloader {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}'''
new_preloader = '''.pixel-preloader {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    transition: opacity 0.8s ease;
}'''
css = css.replace(old_preloader, new_preloader)

# 2. Fix the Window AI Gradient "box" look by adding rounded corners and inset
old_edge = '''/* Elegant Window Edge Gradient (Theme Matched) */
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
}'''
new_edge = '''/* Elegant Window Edge Gradient (Theme Matched) */
.window-ai-gradient {
    position: fixed; /* Fixed to viewport */
    inset: 12px; /* Pulled in from the hard edges */
    z-index: 15;
    pointer-events: none;
    padding: 6px;
    border-radius: 40px; /* Gorgeous rounded corners to kill the 'box' look */
    overflow: hidden;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    /* Soft glowing shadow so it blends perfectly */
    box-shadow: inset 0 0 40px rgba(10, 132, 255, 0.2);
}'''
css = css.replace(old_edge, new_edge)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed CSS edge radius and preloader opacity!")
