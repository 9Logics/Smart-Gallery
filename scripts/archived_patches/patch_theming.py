js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

target = '''    // Fetch data — include month if provided
    let fetchYear = year || new Date().getFullYear();
    let fetchUrl = `/api/recap/generate/${fetchYear}`;
    if (month) fetchUrl += `/${month}`;'''

replacement = '''
    // M3 Expressive Theming & Shapes based on Year
    let fetchYear = year || new Date().getFullYear();
    
    const m3Themes = [
        { primary: '#D0BCFF', surface: '#4A4458', canvas: 'radial-gradient(circle at 50% 50%, #4A4458 0%, #000 100%)' }, // Purple
        { primary: '#FFB59B', surface: '#5D3C28', canvas: 'radial-gradient(circle at 50% 50%, #5D3C28 0%, #000 100%)' }, // Peach
        { primary: '#82D9AD', surface: '#1E4E36', canvas: 'radial-gradient(circle at 50% 50%, #1E4E36 0%, #000 100%)' }, // Mint
        { primary: '#AEC6FF', surface: '#19376D', canvas: 'radial-gradient(circle at 50% 50%, #19376D 0%, #000 100%)' }, // Azure
        { primary: '#FFB4AB', surface: '#690005', canvas: 'radial-gradient(circle at 50% 50%, #690005 0%, #000 100%)' }, // Rose
        { primary: '#E2E25E', surface: '#494A00', canvas: 'radial-gradient(circle at 50% 50%, #494A00 0%, #000 100%)' }  // Lemon
    ];
    
    // Hash year to a theme
    const themeIndex = parseInt(fetchYear) % m3Themes.length;
    const theme = m3Themes[themeIndex];
    
    // Apply CSS Variables
    overlay.style.setProperty('--m3-primary', theme.primary);
    overlay.style.setProperty('--m3-surface', theme.surface);
    const canvas = document.getElementById('m3-aurora-canvas');
    if (canvas) canvas.style.background = theme.canvas;
    
    // Inject Dynamic Year Title (Watermark)
    let watermark = document.getElementById('recap-year-watermark');
    if (!watermark) {
        watermark = document.createElement('div');
        watermark.id = 'recap-year-watermark';
        watermark.style.position = 'absolute';
        watermark.style.top = '32px';
        watermark.style.left = '48px';
        watermark.style.fontFamily = "'Outfit', sans-serif";
        watermark.style.fontSize = '2.5rem';
        watermark.style.fontWeight = '900';
        watermark.style.opacity = '0.5';
        watermark.style.zIndex = '999';
        watermark.style.transition = 'color 0.5s';
        overlay.appendChild(watermark);
    }
    watermark.style.color = theme.primary;
    watermark.innerText = month ? `${month} ${fetchYear}` : fetchYear;
    
    // Replace abstract shapes with massive SVG M3 Expressive paths
    const shapesContainer = document.querySelector('.m3-expressive-shapes');
    if (shapesContainer) {
        shapesContainer.innerHTML = `
            <svg class="m3-svg-shape shape-scallop" viewBox="0 0 100 100" style="position:absolute; width:120vh; height:120vh; top:-10%; right:-10%; opacity:0.04; fill: ${theme.primary}; animation: m3ShapeFloat1 25s infinite alternate ease-in-out;">
                <path d="M50 0 C63.8 0 75 11.2 75 25 C75 25.3 75 25.7 75 26 C88.3 26.5 99 37.6 99 51 C99 64.8 87.8 76 74 76 C73.7 76 73.3 76 73 75.9 C72.5 89.2 61.4 100 48 100 C34.2 100 23 88.8 23 75 C23 74.7 23 74.3 23.1 74 C9.8 73.5 -1 62.4 -1 49 C-1 35.2 10.2 24 24 24 C24.3 24 24.7 24 25 24.1 C25.5 10.8 36.6 0 50 0 Z"></path>
            </svg>
            <svg class="m3-svg-shape shape-star" viewBox="0 0 120 120" style="position:absolute; width:100vh; height:100vh; bottom:-10%; left:-10%; opacity:0.03; fill: ${theme.primary}; animation: m3ShapeFloat2 30s infinite alternate ease-in-out; transform-origin: center;">
                <path d="M 60 5 L 75 30 L 105 30 L 105 60 L 130 75 L 115 100 L 115 130 L 85 130 L 60 155 L 35 130 L 5 130 L 5 100 L -10 75 L 5 50 L 5 20 L 35 20 Z" transform="translate(0, -10)"></path>
            </svg>
        `;
    }

    // Fetch data — include month if provided
    let fetchUrl = `/api/recap/generate/${fetchYear}`;
    if (month) fetchUrl += `/${month}`;
'''
js = js.replace(target, replacement)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Injected M3 Dynamic Theming and Expressive SVGs")
