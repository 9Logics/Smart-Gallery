import os

file_path = 'app/static/style.css'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_css = '''.recap-title {
    font-size: 4.5rem;
    font-weight: 400;
    font-family: 'Pacifico', cursive;
    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 0px 15px rgba(255, 154, 158, 0.4));
    margin: 0;
    padding-right: 10px;
    clip-path: inset(0 100% 0 0);
    opacity: 0;
    transform: rotate(-2deg);
}

body.recap-active .recap-title {
    opacity: 1;
    animation: writeCursive 2s cubic-bezier(0.4, 0, 0.2, 1) 0.8s forwards;
}

@keyframes writeCursive {
    0% { clip-path: inset(0 100% 0 0); }
    100% { clip-path: inset(0 -10% 0 0); }
}'''

new_css = '''.recap-title {
    font-size: 5rem;
    font-weight: 400;
    font-family: 'Abril Fatface', serif;
    background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 4px 15px rgba(255, 255, 255, 0.2));
    margin: 0;
    /* Use extreme negative inset for top, bottom, and left to completely prevent clipping! */
    clip-path: inset(-50% 100% -50% -50%);
    opacity: 0;
    transform: scale(0.95);
    letter-spacing: 0.02em;
}

body.recap-active .recap-title {
    opacity: 1;
    /* Combine the left-to-right wipe with a very subtle scale up for extra premium feel */
    animation: 
        fancyReveal 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.8s forwards,
        fancyScale 3s ease-out 0.8s forwards;
}

@keyframes fancyReveal {
    0% { clip-path: inset(-50% 100% -50% -50%); }
    100% { clip-path: inset(-50% -10% -50% -50%); }
}

@keyframes fancyScale {
    0% { transform: scale(0.95); }
    100% { transform: scale(1); }
}'''

if old_css in content:
    content = content.replace(old_css, new_css)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("CSS updated with premium Abril Fatface effect")
else:
    print("Could not find the old CSS block")
