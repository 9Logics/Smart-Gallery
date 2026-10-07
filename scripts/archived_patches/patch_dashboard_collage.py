import re

js_path = 'app/static/js/recap_dashboard.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

new_block = '''                            const allCovers = Object.values(covers).filter(c => c);
                            if (allCovers.length > 0) {
                                // Shuffle and take up to 3
                                const shuffled = allCovers.sort(() => 0.5 - Math.random());
                                let selected = shuffled.slice(0, 3);
                                while (selected.length < 3 && selected.length > 0) {
                                    selected.push(selected[0]); // duplicate to fill 3 slots if necessary
                                }
                                
                                heroBg.innerHTML = `
                                    <div class="hero-collage-item hero-collage-1" style="background-image: url('/api/photo/file/${encodeURIComponent(selected[0])}')"></div>
                                    <div class="hero-collage-item hero-collage-2" style="background-image: url('/api/photo/file/${encodeURIComponent(selected[1])}')"></div>
                                    <div class="hero-collage-item hero-collage-3" style="background-image: url('/api/photo/file/${encodeURIComponent(selected[2])}')"></div>
                                `;
                                heroBg.style.backgroundImage = 'none';
                                heroBg.style.opacity = '1';
                            }'''

# Find the for loop using regex and replace it
pattern = r'for\s*\(let i = 12;\s*i >= 1;\s*i--\)\s*\{[^\}]+\}\s*\}'
if re.search(pattern, js):
    js = re.sub(pattern, new_block, js)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Successfully replaced with collage!")
else:
    print("Could not find pattern. Here is the block:")
    print(js[500:1500])
