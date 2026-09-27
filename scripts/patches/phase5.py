import re

js_path = r"D:\DevelopmentAppTest Folder\Project Gallery One\app\static\js\recap_player.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# We need to replace the entire C3 animation block
start_c3 = js_code.find("const animName = `customFloat${i}_${Date.now()}`;")
end_c3 = js_code.find("gallery.appendChild(img);", start_c3)

new_c3 = '''
                    // C3: GSAP Physics Float (Skiper 30 / 32 Engine)
                    gallery.appendChild(img);
                    
                    const rotBase = (Math.random() - 0.5) * 40;
                    const driftY = 40 + Math.random() * 40;
                    const driftX = 20 + Math.random() * 20;
                    
                    // Initial state
                    gsap.set(img, {
                        x: 0,
                        y: 0,
                        rotation: rotBase,
                        scale: scale
                    });
                    
                    // Complex elliptical float
                    gsap.to(img, {
                        x: driftX,
                        y: driftY,
                        rotation: rotBase + 5,
                        duration: duration / 2,
                        ease: "sine.inOut",
                        yoyo: true,
                        repeat: -1,
                        delay: delay
                    });
                    
                    gsap.to(img, {
                        x: -driftX * 0.5,
                        rotation: rotBase - 3,
                        duration: duration * 0.8,
                        ease: "sine.inOut",
                        yoyo: true,
                        repeat: -1,
                        delay: delay * 1.5
                    });
                    
'''

js_code = js_code[:start_c3] + new_c3 + js_code[end_c3:]

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)
print("Injected GSAP physics float for background gallery")
