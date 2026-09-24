import os

html_path = 'app/templates/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fallback gradients and Drag-to-Scroll JS
old_js = '''                                // Populate new dashboard thumbnails
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                if (gallery.length > 0) {
                                    document.getElementById('thumb-hero').src = gallery[Math.floor(Math.random() * gallery.length)];
                                    document.querySelectorAll('.rewind-mini-card img').forEach(img => {
                                        img.src = gallery[Math.floor(Math.random() * gallery.length)];
                                    });
                                }'''

new_js = '''                                // Populate new dashboard thumbnails
                                const gallery = Array.from(document.querySelectorAll('.photo-card img')).map(img => img.src);
                                const getFallback = (i) => `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='400'%3E%3Cdefs%3E%3ClinearGradient id='g${i}' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')}'/%3E%3Cstop offset='100%25' stop-color='%23${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')}'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='100%25' height='100%25' fill='url(%23g${i})'/%3E%3C/svg%3E`;
                                
                                document.getElementById('thumb-hero').src = gallery.length > 0 ? gallery[Math.floor(Math.random() * gallery.length)] : getFallback(0);
                                
                                document.querySelectorAll('.rewind-mini-card img').forEach((img, i) => {
                                    img.src = gallery.length > 0 ? gallery[Math.floor(Math.random() * gallery.length)] : getFallback(i + 1);
                                });

                                // Enable Mouse Drag to Scroll
                                document.querySelectorAll('.rewind-row').forEach(row => {
                                    let isDown = false;
                                    let startX;
                                    let scrollLeft;
                                    row.addEventListener('mousedown', (e) => {
                                        isDown = true;
                                        row.style.cursor = 'grabbing';
                                        startX = e.pageX - row.offsetLeft;
                                        scrollLeft = row.scrollLeft;
                                    });
                                    row.addEventListener('mouseleave', () => { isDown = false; row.style.cursor = 'grab'; });
                                    row.addEventListener('mouseup', () => { isDown = false; row.style.cursor = 'grab'; });
                                    row.addEventListener('mousemove', (e) => {
                                        if(!isDown) return;
                                        e.preventDefault();
                                        const x = e.pageX - row.offsetLeft;
                                        const walk = (x - startX) * 2;
                                        row.scrollLeft = scrollLeft - walk;
                                    });
                                });'''

if old_js in html:
    html = html.replace(old_js, new_js)
    html = html.replace('v=262', 'v=263')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed JS Image Fallback and Drag Scrolling!")
else:
    print("Could not find JS block!")


css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix Scrollbars and Base Card Colors
old_css_row = '''/* Horizontal Scroll Rows */
.rewind-row {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding: 10px;
    /* Hide scrollbar for clean look */
    -ms-overflow-style: none;
    scrollbar-width: none;
    scroll-snap-type: x mandatory;
}
.rewind-row::-webkit-scrollbar {
    display: none;
}'''

new_css_row = '''/* Horizontal Scroll Rows */
.rewind-row {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding: 10px 10px 24px 10px; /* Room for scrollbar */
    scroll-snap-type: x mandatory;
    cursor: grab;
}
.rewind-row:active {
    cursor: grabbing;
}
.rewind-row::-webkit-scrollbar {
    height: 8px;
}
.rewind-row::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.05);
    border-radius: 4px;
}
.rewind-row::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.2);
    border-radius: 4px;
}
.rewind-row::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.3);
}'''
css = css.replace(old_css_row, new_css_row)

old_mini_card = '''/* Mini Cards */
.rewind-mini-card {
    position: relative;
    width: 220px;
    height: 140px;'''

new_mini_card = '''/* Mini Cards */
.rewind-mini-card {
    position: relative;
    width: 220px;
    height: 140px;
    background: linear-gradient(135deg, #1c1c1e, #050505); /* Base color */'''
css = css.replace(old_mini_card, new_mini_card)

old_hero_card = '''/* Hero Card */
.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 300px; /* Big cinematic hero */'''

new_hero_card = '''/* Hero Card */
.rewind-hero-card {
    position: relative;
    width: 100%;
    height: 300px; /* Big cinematic hero */
    background: linear-gradient(135deg, #2c2c2e, #1c1c1e); /* Base color */'''
css = css.replace(old_hero_card, new_hero_card)


with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Fixed CSS scrollbars and base card backgrounds!")
