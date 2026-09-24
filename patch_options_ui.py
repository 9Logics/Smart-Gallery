import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update Title Morph
old_morph = '''.recap-container.options-active .rolling-text-title {
    transform: translateY(-35vh) scale(0.35);
    filter: drop-shadow(0px 4px 12px rgba(255, 255, 255, 0.4));
}'''
new_morph = '''.recap-container.options-active .rolling-text-title {
    transform: translateY(-38vh) scale(0.5);
    filter: drop-shadow(0px 4px 20px rgba(255, 255, 255, 0.6));
}'''
if old_morph in css:
    css = css.replace(old_morph, new_morph)

# 2. Update Options UI
old_options = '''.rewind-options {
    position: absolute;
    top: 55%; /* Slightly below center */
    left: 50%;
    transform: translate(-50%, -20%);
    opacity: 0;
    pointer-events: none;
    display: flex;
    gap: 24px;
    z-index: 19;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transition-delay: 0.3s; /* waits for title morph */
}
.recap-container.options-active .rewind-options {
    opacity: 1;
    pointer-events: all;
    transform: translate(-50%, -50%);
}

.rewind-card {
    background: rgba(25, 25, 35, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 28px;
    padding: 32px 24px;
    width: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    backdrop-filter: blur(24px) saturate(150%);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
}
.rewind-card:hover {
    transform: translateY(-10px) scale(1.02);
    background: rgba(35, 35, 45, 0.6);
    border-color: rgba(10, 132, 255, 0.5); /* Apple Blue subtle highlight */
}

.rewind-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    color: var(--accent-color);
}
.rewind-icon svg {
    width: 28px;
    height: 28px;
}

.rewind-card h3 {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: #fff;
    font-family: var(--font-display);
}
.rewind-card p {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.6);
    margin: 0 0 24px 0;
    min-height: 40px;
}

.rewind-select {
    width: 100%;
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.15);
    color: #fff;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 1rem;
    margin-bottom: 20px;
    outline: none;
    appearance: none;
    cursor: pointer;
    font-family: var(--font-sans);
}
.rewind-select:focus {
    border-color: var(--accent-color);
}
.rewind-select option {
    background: #111;
    color: #fff;
}

.rewind-play-btn {
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    transition: transform 0.2s, filter 0.2s;
}
.rewind-play-btn:active {
    transform: scale(0.95);
}
.rewind-card .btn-primary {
    background: var(--accent-color);
    color: #fff;
    box-shadow: 0 4px 15px rgba(10, 132, 255, 0.4);
}
.rewind-card .btn-primary:hover {
    filter: brightness(1.1);
}
.rewind-card .btn-secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
}
.rewind-card .btn-secondary:hover {
    background: rgba(255,255,255,0.15);
}'''

new_options = '''.rewind-options {
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -15%);
    opacity: 0;
    pointer-events: none;
    display: flex;
    gap: 32px;
    z-index: 19;
    transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    transition-delay: 0.3s;
}
.recap-container.options-active .rewind-options {
    opacity: 1;
    pointer-events: all;
    transform: translate(-50%, -45%);
}

.rewind-card {
    background: rgba(20, 20, 30, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 32px;
    padding: 40px 32px;
    width: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    backdrop-filter: blur(40px) saturate(200%);
    transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.15);
}
.rewind-card:hover {
    transform: translateY(-12px) scale(1.03);
    background: rgba(30, 30, 45, 0.7);
    border-color: rgba(10, 132, 255, 0.6);
}

.rewind-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(10,132,255,0.2), rgba(10,132,255,0.05));
    border: 1px solid rgba(10,132,255,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    color: var(--accent-color);
}
.rewind-icon svg {
    width: 32px;
    height: 32px;
}

.rewind-card h3 {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0 0 10px 0;
    color: #fff;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
}
.rewind-card p {
    font-size: 1rem;
    color: rgba(255,255,255,0.5);
    margin: 0 0 32px 0;
    line-height: 1.4;
    min-height: 45px;
    font-family: var(--font-sans);
}

.rewind-select-wrap {
    width: 100%;
    position: relative;
    margin-bottom: 12px;
}
.rewind-select {
    width: 100%;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
    padding: 16px 20px;
    border-radius: 16px;
    font-size: 1.05rem;
    font-weight: 500;
    outline: none;
    appearance: none;
    cursor: pointer;
    font-family: var(--font-sans);
    transition: border-color 0.2s, background 0.2s;
    text-align: center;
}
.rewind-select:hover {
    background: rgba(255,255,255,0.08);
}
.rewind-select:focus {
    border-color: var(--accent-color);
    background: rgba(255,255,255,0.1);
}
.rewind-select option {
    background: #111;
    color: #fff;
}
/* Down arrow for select */
.rewind-select-wrap::after {
    content: "▼";
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    pointer-events: none;
}

.rewind-play-btn {
    width: 100%;
    padding: 16px;
    border-radius: 16px;
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
    border: none;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s, box-shadow 0.2s;
    font-family: var(--font-sans);
}
.rewind-play-btn:active {
    transform: scale(0.95);
}
.rewind-card .btn-primary {
    background: var(--accent-color);
    color: #fff;
    box-shadow: 0 8px 24px rgba(10, 132, 255, 0.3);
}
.rewind-card .btn-primary:hover {
    background: #1a8eff;
    box-shadow: 0 12px 32px rgba(10, 132, 255, 0.5);
}
.rewind-card .btn-secondary {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.1);
}
.rewind-card .btn-secondary:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.2);
}'''

if old_options in css:
    css = css.replace(old_options, new_options)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed CSS!")
else:
    print("Could not find CSS!")


html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Wrap selects in .rewind-select-wrap for the custom arrow
old_html_select1 = '''<select class="rewind-select">
                    <option value="" disabled selected>Select Month</option>'''
new_html_select1 = '''<div class="rewind-select-wrap"><select class="rewind-select">
                    <option value="" disabled selected>Select Month</option>'''
old_html_select1_end = '''<option>April 2026</option>
                </select>'''
new_html_select1_end = '''<option>April 2026</option>
                </select></div>'''

old_html_select2 = '''<select class="rewind-select">
                    <option value="" disabled selected>Select Year</option>'''
new_html_select2 = '''<div class="rewind-select-wrap"><select class="rewind-select">
                    <option value="" disabled selected>Select Year</option>'''
old_html_select2_end = '''<option>2023</option>
                </select>'''
new_html_select2_end = '''<option>2023</option>
                </select></div>'''

html = html.replace(old_html_select1, new_html_select1)
html = html.replace(old_html_select1_end, new_html_select1_end)
html = html.replace(old_html_select2, new_html_select2)
html = html.replace(old_html_select2_end, new_html_select2_end)
html = html.replace('v=257', 'v=258')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed HTML!")

