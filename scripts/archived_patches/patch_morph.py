import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

s1 = "M 100.0 50.0 C 100.0 54.0, 84.5 57.0, 83.3 60.8 C 82.1 64.6, 92.8 76.2, 90.5 79.4 C 88.1 82.6, 73.8 76.0, 70.6 78.3 C 67.4 80.7, 69.2 96.3, 65.5 97.6 C 61.7 98.8, 54.0 85.0, 50.0 85.0 C 46.0 85.0, 38.3 98.8, 34.5 97.6 C 30.8 96.3, 32.6 80.7, 29.4 78.3 C 26.2 76.0, 11.9 82.6, 9.5 79.4 C 7.2 76.2, 17.9 64.6, 16.7 60.8 C 15.5 57.0, 0.0 54.0, 0.0 50.0 C -0.0 46.0, 15.5 43.0, 16.7 39.2 C 17.9 35.4, 7.2 23.8, 9.5 20.6 C 11.9 17.4, 26.2 24.0, 29.4 21.7 C 32.6 19.3, 30.8 3.7, 34.5 2.4 C 38.3 1.2, 46.0 15.0, 50.0 15.0 C 54.0 15.0, 61.7 1.2, 65.5 2.4 C 69.2 3.7, 67.4 19.3, 70.6 21.7 C 73.8 24.0, 88.1 17.4, 90.5 20.6 C 92.8 23.8, 82.1 35.4, 83.3 39.2 C 84.5 43.0, 100.0 46.0, 100.0 50.0 Z"
s2 = "M 100.0 50.0 C 100.0 56.2, 95.7 58.3, 93.7 64.2 C 91.8 70.1, 94.1 74.4, 90.5 79.4 C 86.8 84.4, 82.1 83.6, 77.0 87.2 C 72.0 90.9, 71.4 95.6, 65.5 97.6 C 59.5 99.5, 56.2 96.0, 50.0 96.0 C 43.8 96.0, 40.5 99.5, 34.5 97.6 C 28.6 95.6, 28.0 90.9, 23.0 87.2 C 17.9 83.6, 13.2 84.4, 9.5 79.4 C 5.9 74.4, 8.2 70.1, 6.3 64.2 C 4.3 58.3, 0.0 56.2, 0.0 50.0 C -0.0 43.8, 4.3 41.7, 6.3 35.8 C 8.2 29.9, 5.9 25.6, 9.5 20.6 C 13.2 15.6, 17.9 16.4, 23.0 12.8 C 28.0 9.1, 28.6 4.4, 34.5 2.4 C 40.5 0.5, 43.8 4.0, 50.0 4.0 C 56.2 4.0, 59.5 0.5, 65.5 2.4 C 71.4 4.4, 72.0 9.1, 77.0 12.8 C 82.1 16.4, 86.8 15.6, 90.5 20.6 C 94.1 25.6, 91.8 29.9, 93.7 35.8 C 95.7 41.7, 100.0 43.8, 100.0 50.0 Z"
s3 = "M 100.0 50.0 C 100.0 54.7, 99.0 61.0, 97.6 65.5 C 96.1 69.9, 93.2 75.6, 90.5 79.4 C 87.7 83.2, 83.2 87.7, 79.4 90.5 C 75.6 93.2, 69.9 96.1, 65.5 97.6 C 61.0 99.0, 54.7 100.0, 50.0 100.0 C 45.3 100.0, 39.0 99.0, 34.5 97.6 C 30.1 96.1, 24.4 93.2, 20.6 90.5 C 16.8 87.7, 12.3 83.2, 9.5 79.4 C 6.8 75.6, 3.9 69.9, 2.4 65.5 C 1.0 61.0, 0.0 54.7, 0.0 50.0 C -0.0 45.3, 1.0 39.0, 2.4 34.5 C 3.9 30.1, 6.8 24.4, 9.5 20.6 C 12.3 16.8, 16.8 12.3, 20.6 9.5 C 24.4 6.8, 30.1 3.9, 34.5 2.4 C 39.0 1.0, 45.3 0.0, 50.0 0.0 C 54.7 -0.0, 61.0 1.0, 65.5 2.4 C 69.9 3.9, 75.6 6.8, 79.4 9.5 C 83.2 12.3, 87.7 16.8, 90.5 20.6 C 93.2 24.4, 96.1 30.1, 97.6 34.5 C 99.0 39.0, 100.0 45.3, 100.0 50.0 Z"

# I will replace the previously inserted svg strings
new_svg_block = f'''        shapesContainer.innerHTML = `
            <!-- First Morpher: Top Right -->
            <svg class="m3-svg-shape shape-scallop" viewBox="0 0 100 100" style="position:absolute; width:120vh; height:120vh; top:-10%; right:-10%; opacity:0.04; fill: ${{theme.primary}}; animation: m3ShapeFloat1 25s infinite alternate ease-in-out;">
                <path d="{s1}">
                    <animate attributeName="d" dur="15s" repeatCount="indefinite" values="{s1}; {s2}; {s3}; {s2}; {s1}" keyTimes="0; 0.25; 0.5; 0.75; 1" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1" />
                </path>
            </svg>
            
            <!-- Second Morpher: Bottom Left -->
            <svg class="m3-svg-shape shape-star" viewBox="0 0 100 100" style="position:absolute; width:100vh; height:100vh; bottom:-10%; left:-10%; opacity:0.03; fill: ${{theme.primary}}; animation: m3ShapeFloat2 30s infinite alternate ease-in-out; transform-origin: center;">
                <path d="{s2}">
                    <animate attributeName="d" dur="12s" repeatCount="indefinite" values="{s2}; {s1}; {s2}; {s3}; {s2}" keyTimes="0; 0.25; 0.5; 0.75; 1" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1; 0.4 0 0.2 1" />
                </path>
            </svg>
        `;'''

# Using regex to replace the shapesContainer.innerHTML block
js = re.sub(r'shapesContainer\.innerHTML = `.*?`;', new_svg_block, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Injected morphing SVG attributes")
