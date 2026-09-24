import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# I will find the function generateYearlyTheme and rewrite the start of it
def rewrite_theme(match):
    prefix = match.group(1)
    return prefix + '''    // Pick ONE solid theme color for the entire year
    const themeColors = [
        '#FF0A54', '#00BBF9', '#FEE440', '#00F5D4', '#9B5DE5', '#FA709A', '#8AC926', '#1982C4', '#FF595E'
    ];
    const themeColor = themeColors[Math.floor(myRand() * themeColors.length)];
    const styleType = Math.floor(myRand() * 3);'''

# Find from "const myRand" to "if (styleType === 0) {"
pattern = r"(const myRand = \(\) => \{.*?\};\s*)(const palettes = \[.*?\];\s*const palette = .*?;\s*const styleType = Math\.floor\(myRand\(\) \* 3\);)"

js = re.sub(pattern, rewrite_theme, js, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Regex patch applied for themeColor!")
