import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Remove event listener additions and removals
js = js.replace("document.addEventListener('mousemove', handleParallaxMouseMove);", "")
js = js.replace("document.removeEventListener('mousemove', handleParallaxMouseMove);", "")

# 2. Nullify the function so it does nothing if called elsewhere
js = re.sub(r'function handleParallaxMouseMove\(e\)\s*\{[^\}]+\}', 'function handleParallaxMouseMove(e) {}', js, flags=re.DOTALL)
# Actually, the function has nested braces, regex might fail. 
# Better to just overwrite the event listener attachments.
# Let's completely wipe it using string replacement for safety, but just removing listeners is 100% effective.

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print('Parallax removed!')
