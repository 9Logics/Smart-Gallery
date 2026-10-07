import re

with open('app/app_core.py', 'r', encoding='utf-8') as f:
    py = f.read()

target = """scan_status = {'status': 'idle', 'processed': 0, 'total': 0, 'current_file':
    '', 'phase': '', 'cancel_requested': False}
geocode_lock = threading.Lock()"""

replacement = """scan_status = {'status': 'idle', 'processed': 0, 'total': 0, 'current_file':
    '', 'phase': '', 'cancel_requested': False}
scan_queue = []
scan_queue_lock = threading.Lock()
queue_worker_running = False

def start_queue_worker():
    global queue_worker_running
    with scan_queue_lock:
        if queue_worker_running:
            return
        queue_worker_running = True
        
    def worker():
        global queue_worker_running
        while True:
            with scan_queue_lock:
                if not scan_queue:
                    queue_worker_running = False
                    return
                # Peek the next job (don't pop yet)
                current_job = scan_queue[0]
            
            try:
                current_job['func']()
            except Exception as e:
                print(f"Queue job {current_job['type']} failed: {e}")
            
            with scan_queue_lock:
                # Remove the job we just finished from the queue
                if scan_queue:
                    scan_queue.pop(0)

    threading.Thread(target=worker, daemon=True).start()

def queue_scan(scan_type, target_func):
    with scan_queue_lock:
        # Prevent queueing the same scan type if it's already in the queue
        for item in scan_queue:
            if item['type'] == scan_type:
                return False
        
        # If queue is empty but a scan is CURRENTLY running, the status is not idle.
        # Wait, if status is idle and queue is empty, we still queue it and the worker will pick it up immediately.
        # But to enforce "only one scan type can be queued at once", we also shouldn't allow queueing if that scan type is CURRENTLY running!
        # Actually, let's just use the queue for EVERYTHING!
        # Even the currently running scan will be in the queue (at index 0).
        # We only pop it AFTER it finishes.
        
        # Check if already in queue
        if any(job['type'] == scan_type for job in scan_queue):
            return False
            
        scan_queue.append({'type': scan_type, 'func': target_func})
    
    start_queue_worker()
    return True

geocode_lock = threading.Lock()"""

if target in py:
    py = py.replace(target, replacement)
    with open('app/app_core.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print("Patched app_core.py with scan queue logic")
else:
    print("Target not found in app_core.py")
