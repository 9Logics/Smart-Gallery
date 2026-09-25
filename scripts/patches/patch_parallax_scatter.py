import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

old_scatter = '''                    const size = 150 + Math.random() * 250; 
                    const posX = Math.random() * 85; 
                    const posY = Math.random() * 85; 
                    const delay = Math.random() * -30; 
                    const duration = 20 + Math.random() * 20; 
                    const rot = (Math.random() - 0.5) * 50; 
                    
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*80 - 40)}px`;
                    img.style.left = `${posX}vw`;
                    img.style.top = `${posY}vh`;
                    img.style.opacity = '0.35';
                    img.style.zIndex = Math.floor(Math.random() * 10);'''

new_scatter = '''                    // More intelligent space filling (using % instead of vw/vh since container is 140%)
                    const size = 150 + Math.random() * 200; 
                    const posX = -5 + Math.random() * 95; // %
                    const posY = -5 + Math.random() * 95; // %
                    const delay = Math.random() * -30; 
                    const duration = 20 + Math.random() * 20; 
                    const rot = (Math.random() - 0.5) * 50; 
                    
                    img.style.position = 'absolute';
                    img.style.width = `${size}px`;
                    img.style.height = `${size + (Math.random()*80 - 40)}px`;
                    img.style.left = `${posX}%`;
                    img.style.top = `${posY}%`;
                    img.style.opacity = '0.35';
                    img.style.zIndex = Math.floor(Math.random() * 10);'''

js = js.replace(old_scatter, new_scatter)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated JS scatter logic!")
