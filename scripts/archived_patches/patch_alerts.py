import os
import re

directories = ['app/static/js', 'app/static/js/views']

for directory in directories:
    for filename in os.listdir(directory):
        if not filename.endswith('.js'):
            continue
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        
        # 1. Replace alert( with appAlert(
        # Negative lookbehind to avoid replacing appAlert( again
        content = re.sub(r'(?<!app)alert\(', 'appAlert(', content)
        
        # 2. Replace confirm( with await appConfirm(
        # Exclude the definition of appConfirm itself
        content = re.sub(r'(?<!app)(?<!resolve\()confirm\(', 'await appConfirm(', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {filepath}")
