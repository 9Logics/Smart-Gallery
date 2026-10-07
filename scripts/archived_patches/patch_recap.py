js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix skiper-47
js = js.replace('while (deck.length < 7) {', 'while (deck.length < 15) {')
# Fix skiper-54
js = js.replace('while (deck.length < 5) {', 'while (deck.length < 15) {')

# Remove the aggressive slice limits that are breaking the loop length
js = js.replace('deck = deck.slice(0, 15);', 'deck = deck.slice(0, 24);')

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched loop lengths in recap_player.js")
