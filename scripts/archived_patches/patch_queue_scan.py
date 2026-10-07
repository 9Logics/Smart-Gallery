import re

with open('app/routes/scan.py', 'r', encoding='utf-8') as f:
    py = f.read()

target_status = """@scan_bp.route('/api/scan/status')
def get_scan_status():
    return jsonify(scan_status)"""

replacement_status = """@scan_bp.route('/api/scan/status')
def get_scan_status():
    import copy
    from app.app_core import scan_queue, scan_queue_lock
    status = copy.deepcopy(scan_status)
    with scan_queue_lock:
        # Subtract 1 because index 0 is the CURRENTLY running scan
        # We only want to show the number of scans waiting in the queue.
        # But if nothing is running, queue is empty.
        q_count = len(scan_queue) - 1 if len(scan_queue) > 0 else 0
        status['queue_count'] = q_count
    return jsonify(status)"""

py = py.replace(target_status, replacement_status)

target_manual = """    def scan_task():
        scan_directory(root_dir)
    threading.Thread(target=scan_task, daemon=True).start()
    return jsonify({'success': True, 'message': 'Directory scan started'})"""

replacement_manual = """    def scan_task():
        scan_directory(root_dir)
    from app.app_core import queue_scan
    added = queue_scan('full_scan', scan_task)
    if not added:
        return jsonify({'success': True, 'message': 'Full scan is already queued or running'})
    return jsonify({'success': True, 'message': 'Directory scan queued'})"""

py = py.replace(target_manual, replacement_manual)

target_track = """    import threading
    thread = threading.Thread(target=track_task)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'})"""

replacement_track = """    from app.app_core import queue_scan
    added = queue_scan('track_moved', track_task)
    if not added:
        return jsonify({'status': 'already_queued'})
    return jsonify({'status': 'started'})"""

py = py.replace(target_track, replacement_track)

target_hero = """    threading.Thread(target=hero_scan_task, daemon=True).start()
    return jsonify({'success': True})"""

replacement_hero = """    from app.app_core import queue_scan
    added = queue_scan('hero_ai', hero_scan_task)
    if not added:
        return jsonify({'success': True, 'message': 'Hero AI scan already queued'})
    return jsonify({'success': True})"""

py = py.replace(target_hero, replacement_hero)

with open('app/routes/scan.py', 'w', encoding='utf-8') as f:
    f.write(py)
print("Patched scan.py")
