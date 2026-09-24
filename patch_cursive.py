import os

file_path = 'app/static/style.css'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_css = '''.recap-title {
    font-size: 3rem;
    font-weight: 800;
    font-family: system-ui, -apple-system, sans-serif;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #ff00cc, #3333ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 1s ease 0.8s, transform 1s ease 0.8s;
}

body.recap-active .recap-title {
    opacity: 1;
    transform: translateY(0);
}'''

new_css = '''.recap-title {
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

if old_css in content:
    content = content.replace(old_css, new_css)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("CSS updated with cursive writing effect")
else:
    print("Could not find the old CSS block")
