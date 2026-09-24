import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the text string
old_text = 'const text = "Your 2026 Rewind";'
new_text = 'const text = "Your Rewinds";'

if old_text in html:
    html = html.replace(old_text, new_text)

# 2. Update the wipe timing
old_js = '''                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * 15); // slightly slower to see the shatter effect
                        });
                        
                        setTimeout(() => {
                            preloader.style.display = 'none';
                        }, blocks.length * 15 + 100);'''

new_js = '''                        const totalDuration = 800; // Wipe finishes in 0.8s total
                        const staggerDelay = totalDuration / blocks.length;

                        blocks.forEach((block, i) => {
                            setTimeout(() => {
                                block.style.opacity = '0';
                            }, i * staggerDelay);
                        });
                        
                        setTimeout(() => {
                            preloader.style.display = 'none';
                        }, totalDuration + 100);'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=250', 'v=251')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed timing and text!")
else:
    print("Could not find JS block to fix!")
