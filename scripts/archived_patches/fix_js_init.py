import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Remove the old iconic_place block and inject the top_places initialization
# The block starts with "if (data.iconic_place)" and ends before "// Skiper 30 Parallax Gallery"
js = re.sub(
    r'if\s*\(data\.iconic_place\).*?(?=// Skiper 30 Parallax Gallery)',
    '''if (data.top_places && data.top_places.length > 0) {
                buildPlacesAccordion(data.top_places);
            } else {
                const s = document.getElementById('slide-top-places');
                if (s) s.style.display = 'none';
            }
            
            ''',
    js,
    flags=re.DOTALL
)

# 2. Remove the heroContainer block
# The block starts with "const heroContainer = document.getElementById('hero-moment-container');"
# and ends right before "}" that closes the if (data.gallery_photos) or whatever block it was in.
# Let's find "const heroContainer =" and remove it up to the end of that block.
# Actually, since it uses heroContainer.style.display, we can just replace that line with a no-op if it exists.
# Let's be safer.
js = re.sub(
    r'const heroContainer = document\.getElementById\(\'hero-moment-container\'\);.*?heroContainer\.appendChild\(collage\);\s*\} else if \(mPhotos\.length > 0\) \{.*?\}\s*\}',
    '',
    js,
    flags=re.DOTALL
)

# Also remove any remaining heroContainer references if the regex missed part of the fallback
js = re.sub(
    r'const heroContainer = document\.getElementById\(\'hero-moment-container\'\).*?(?=\n\s*// Finish loader)',
    '',
    js,
    flags=re.DOTALL
)


with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Regex patched initSkiper54Carousel and heroContainer out of recap_player.js")
