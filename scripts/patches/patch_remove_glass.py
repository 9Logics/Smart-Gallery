import os
import re

css_path = 'app/static/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the `#recap-ai-comment` block
old_block_pattern = r"#recap-ai-comment \{.*?box-shadow: 0 20px 40px rgba\(0,0,0,0\.3\);\n\}"

new_block = '''#recap-ai-comment {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 2.8rem !important;
    line-height: 1.4;
    color: #111;
    transform: rotate(-2deg);
    padding: 25px 35px;
    background: #fff;
    border: 3px solid #111;
    border-radius: 4px;
    max-width: 80%;
    margin: 0 auto;
    box-shadow: 8px 8px 0px #111;
}'''

css = re.sub(old_block_pattern, new_block, css, flags=re.DOTALL)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print("Removed glass effect and changed font to Outfit for recap-ai-comment!")
