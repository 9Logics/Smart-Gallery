import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the old palettes and styleType block with the new themeColor logic
old_block_pattern = r"const palettes = \[\s*\[.*?\]\s*\];\s*const palette = palettes\[Math\.floor\(myRand\(\) \* palettes\.length\)\];"

new_block = '''// Pick ONE solid theme color for the entire year
    const themeColors = [
        '#FF0A54', // Crimson
        '#00BBF9', // Cyan
        '#FEE440', // Yellow
        '#00F5D4', // Mint
        '#9B5DE5', // Purple
        '#FA709A', // Pink
        '#8AC926', // Lime
        '#1982C4', // Blue
        '#FF595E'  // Coral
    ];
    const themeColor = themeColors[Math.floor(myRand() * themeColors.length)];'''

js = re.sub(old_block_pattern, new_block, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched themeColor definition in recap_player.js!")
