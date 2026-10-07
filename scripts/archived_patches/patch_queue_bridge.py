import re

with open('app/bridge_api.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """    def get_scan_status(self):
        \"\"\"Replaces: GET /api/scan/status\"\"\"
        import copy
        return copy.deepcopy(scan_status)"""

replacement = """    def get_scan_status(self):
        \"\"\"Replaces: GET /api/scan/status\"\"\"
        import copy
        status = copy.deepcopy(scan_status)
        from app.app_core import scan_queue, scan_queue_lock
        with scan_queue_lock:
            q_count = len(scan_queue) - 1 if len(scan_queue) > 0 else 0
            status['queue_count'] = q_count
        return status"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/bridge_api.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched bridge_api.py")
else:
    print("Target not found in bridge_api.py")
