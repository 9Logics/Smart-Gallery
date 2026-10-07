import re

js_path = 'app/static/js/recap_dashboard.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the monthGradients array with M3 Tonal colors
old_gradients_regex = r"const monthGradients = \[[^\]]+\];"
m3_gradients = '''const monthGradients = [
                            'linear-gradient(135deg, #2D1A43, #1D192B)', // M3 Purple
                            'linear-gradient(135deg, #102636, #101E28)', // M3 Blue/Cyan
                            'linear-gradient(135deg, #132C20, #112118)', // M3 Green
                            'linear-gradient(135deg, #431720, #2C151A)', // M3 Red
                            'linear-gradient(135deg, #432100, #2D1600)', // M3 Orange
                            'linear-gradient(135deg, #15263A, #0F1D2A)', // M3 Indigo
                            'linear-gradient(135deg, #2D1A43, #1D192B)',
                            'linear-gradient(135deg, #102636, #101E28)',
                            'linear-gradient(135deg, #132C20, #112118)',
                            'linear-gradient(135deg, #431720, #2C151A)',
                            'linear-gradient(135deg, #432100, #2D1600)',
                            'linear-gradient(135deg, #15263A, #0F1D2A)'
                        ];'''

js = re.sub(old_gradients_regex, m3_gradients, js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated monthGradients to M3 Tonal colors")
