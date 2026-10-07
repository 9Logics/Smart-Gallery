import re

with open('app.py', 'r', encoding='utf-8') as f:
    d = f.read()

target = "webview.start(debug=args.dev)"
replacement = "webview.start(debug=args.dev, private_mode=False)"

if target in d:
    d = d.replace(target, replacement)
    print("Successfully patched app.py")
else:
    print("WARNING: target not found")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(d)
