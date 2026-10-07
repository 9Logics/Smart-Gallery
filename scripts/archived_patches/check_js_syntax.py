import os
import subprocess

directories = ['app/static/js', 'app/static/js/views']

for directory in directories:
    for filename in os.listdir(directory):
        if not filename.endswith('.js'):
            continue
        filepath = os.path.join(directory, filename)
        result = subprocess.run(['node', '-c', filepath], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error in {filepath}: {result.stderr.splitlines()[0]}")
