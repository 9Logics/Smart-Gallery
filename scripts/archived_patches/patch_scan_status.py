import re

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """def scan_directory(root_dir):
    global scan_status
    print(f'Starting phased scan of: {root_dir}')"""

replacement = """def scan_directory(root_dir):
    global scan_status
    with scan_lock:
        scan_status['status'] = 'scanning'
        scan_status['cancel_requested'] = False
        scan_status['processed'] = 0
        scan_status['total'] = 0
        scan_status['current_file'] = ''
        scan_status['phase'] = 'Scanning directories'
    print(f'Starting phased scan of: {root_dir}')"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/app_core.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched scan_directory to set status to scanning")
else:
    print("Target not found in app_core.py")
