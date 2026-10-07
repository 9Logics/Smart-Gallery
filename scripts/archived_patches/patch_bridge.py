import os

app_path = 'app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the entire if args.bridge block with a pass
target = "if args.bridge:"
replacement = """if args.bridge:
        print("Native Bridge Mode was requested, but user requested no Edge/WebView2. Falling back to Chrome App Mode...")
        # We purposely bypass webview since it forces Edge Chromium on Windows.
        pass

    # Dummy block so we can safely delete the old block below"""

# We'll use regex to chop out everything from `if args.bridge:` down to `import os` before WERKZEUG check
import re
new_code = re.sub(r'    if args\.bridge:.*?    import os\n    # If we are NOT', replacement + '\n\n    import os\n    # If we are NOT', code, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Updated bridge")
