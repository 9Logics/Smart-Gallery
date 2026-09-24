import os

# --- Update HTML JS Logic ---
html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_js = '''                // Simulate Loading for Pixel Preloader
                let count = 0;
                const interval = setInterval(() => {
                    count += Math.floor(Math.random() * 20) + 10;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        
                        // Pixel Wipe Animation (slef.me style)
                        counter.style.opacity = '0';
                        const blocks = Array.from(grid.children);
                        // Shuffle array for random pixel disappearance
                        blocks.sort(() => Math.random() - 0.5);
                        
                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * 8); // extremely fast granular reveal
                        });
                        
                        // Wait for grid to finish wiping, then reveal text
                        setTimeout(() => {
                            preloader.style.display = 'none';
                            title.classList.add('revealed');
                        }, blocks.length * 8 + 100);
                    }
                    counter.innerText = count + '%';
                }, 80);'''

new_js = '''                // Simulate Loading for Pixel Preloader
                let count = 0;
                const interval = setInterval(() => {
                    count += Math.floor(Math.random() * 10) + 5;
                    if (count >= 100) {
                        count = 100;
                        clearInterval(interval);
                        
                        // Pixel Wipe Animation (slef.me style)
                        counter.style.opacity = '0';
                        const blocks = Array.from(grid.children);
                        // Shuffle array for random pixel disappearance
                        blocks.sort(() => Math.random() - 0.5);
                        
                        // Start text reveal underneath the pixels!
                        title.classList.add('revealed');

                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * 15); // slightly slower to see the shatter effect
                        });
                        
                        setTimeout(() => {
                            preloader.style.display = 'none';
                        }, blocks.length * 15 + 100);
                    }
                    counter.innerText = count + '%';
                }, 100);'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=248', 'v=249')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS timing!")
else:
    print("Could not find JS block!")


# --- Update CSS Background ---
css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_recap_bg = '''    height: 100vh;
    background: #050505;
    z-index: 9999;'''

new_recap_bg = '''    height: 100vh;
    background: radial-gradient(circle at center, #1a1a2e 0%, #050505 100%);
    z-index: 9999;'''

if old_recap_bg in css:
    css = css.replace(old_recap_bg, new_recap_bg)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("Fixed CSS background!")
else:
    print("Could not find CSS background!")
