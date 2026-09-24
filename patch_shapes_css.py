import os

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update `#theme-canvas` to remove opacity and mix-blend-mode
css = css.replace('opacity: 0.6;', 'opacity: 1;')

# 2. Update `.theme-blob` to be solid (for Goopy Circles)
css = css.replace('mix-blend-mode: screen;', '')

# 3. Update `.theme-orb` to be a Morphing Blob instead of a blur
new_orb = '''
.theme-orb {
    position: absolute;
    width: 60vh;
    height: 60vh;
    border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
    animation: morphBlob 15s infinite alternate ease-in-out;
}

@keyframes morphBlob {
    0% { transform: translate(-10vw, -10vh) rotate(0deg); border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%; }
    50% { transform: translate(30vw, 30vh) rotate(180deg); border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    100% { transform: translate(80vw, 80vh) rotate(360deg); border-radius: 30% 70% 50% 50% / 50% 40% 70% 60%; }
}
'''

# We need to replace the old `.theme-orb` and `@keyframes moveOrb`
import re
css = re.sub(r'\.theme-orb\s*\{[^}]*\}', '', css)
css = re.sub(r'@keyframes moveOrb\s*\{[^}]*\}', '', css)

# 4. Inject the new morphing blob css
css += '\n' + new_orb

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated CSS to remove glows and add solid morphing blobs!")
