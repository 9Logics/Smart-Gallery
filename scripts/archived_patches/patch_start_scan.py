import re

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """def start_scan_thread(root_dir):
    global scan_status
    with scan_lock:
        if scan_status['status'] == 'scanning':
            return False
        scan_status['status'] = 'scanning'
        scan_status['cancel_requested'] = False
        scan_status['processed'] = 0
        scan_status['total'] = 0
        scan_status['current_file'] = ''
    thread = threading.Thread(target=scan_directory, args=(root_dir,))
    thread.daemon = True
    thread.start()
    return True"""

replacement = """def start_scan_thread(root_dir):
    def scan_task():
        scan_directory(root_dir)
    return queue_scan('full_scan', scan_task)"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/app_core.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched start_scan_thread in app_core.py")
else:
    print("Target not found in app_core.py")
