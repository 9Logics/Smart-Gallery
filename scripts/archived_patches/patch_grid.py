import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# We need to replace the marquee block.
# Look for: if (mPhotos.length > 0) { ... wrapper.appendChild(row2); ... heroContainer.appendChild(wrapper); }
start_str = "if (mPhotos.length > 0) {"
end_str = "heroContainer.appendChild(wrapper);\n                    }"

# Find indices
start_idx = js.find(start_str)
end_idx = js.find(end_str)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_str)
    
    new_code = '''if (mPhotos.length >= 4) {
                        const collage = document.createElement('div');
                        collage.className = 'hero-grid-collage';
                        
                        const classes = ['item-main', 'item-top', 'item-bl', 'item-br'];
                        const photos = mPhotos.slice(0, 4); // Take exact 4
                        
                        photos.forEach((p, i) => {
                            const div = document.createElement('div');
                            div.className = 'grid-item ' + classes[i];
                            div.innerHTML = \<img src="/api/photo/file/\" />\;
                            collage.appendChild(div);
                        });
                        
                        heroContainer.appendChild(collage);
                    } else if (mPhotos.length > 0) {
                        // Fallback if less than 4 photos
                        heroContainer.innerHTML = \<div class="hero-grid-collage single-item"><img src="/api/photo/file/\" style="width:100%; height:100%; object-fit:cover;" /></div>\;
                    }'''
                    
    js = js[:start_idx] + new_code + js[end_idx:]
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Replaced marquee with Grid Collage in JS")
else:
    print("Could not find the marquee block to replace")
