import re

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """            with scan_queue_lock:
                # Remove the job we just finished from the queue
                if scan_queue:
                    scan_queue.pop(0)"""

replacement = """            with scan_queue_lock:
                # Remove the job we just finished from the queue
                if scan_queue:
                    scan_queue.pop(0)
                
                # Safeguard: Keep status as scanning if there's another job in the queue
                # so the frontend poller doesn't prematurely terminate.
                if scan_queue:
                    scan_status['status'] = 'scanning'
                    scan_status['phase'] = 'Starting next job...'"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/app_core.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched queue loop safeguard")
else:
    print("Target not found in app_core.py")
