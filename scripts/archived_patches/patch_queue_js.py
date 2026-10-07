import re

with open('app/static/js/scanner.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """                    document.getElementById('slideout-count').innerText = `${data.processed}/${data.total}`;
                    document.getElementById('slideout-pct').innerText = `(${pct}%)`;
                    document.getElementById('slideout-bar-fill').style.width = `${pct}%`;
                }"""

replacement = """                    document.getElementById('slideout-count').innerText = `${data.processed}/${data.total}`;
                    document.getElementById('slideout-pct').innerText = `(${pct}%)`;
                    document.getElementById('slideout-bar-fill').style.width = `${pct}%`;
                    
                    const qIndicator = document.getElementById('slideout-queue-indicator');
                    if (qIndicator) {
                        if (data.queue_count > 0) {
                            qIndicator.classList.remove('hidden');
                            document.getElementById('slideout-queue-count').innerText = `${data.queue_count} in queue`;
                        } else {
                            qIndicator.classList.add('hidden');
                        }
                    }
                }"""

if target in js:
    js = js.replace(target, replacement)
    
    # Also fix pollScanStatus to continue polling if there are items in queue even if status is idle?
    # Wait, if status is idle, we don't show the wrapper.
    # But if queue > 0, the worker should start scanning immediately.
    # We should poll if queue_count > 0 OR status === 'scanning'.
    
    target2 = """            // Queue next poll ONLY if scanning
            if (data.status === 'scanning') {
                setTimeout(pollScanStatus, 250);
            }"""
    
    replacement2 = """            // Queue next poll ONLY if scanning or queued
            if (data.status === 'scanning' || data.queue_count > 0) {
                setTimeout(pollScanStatus, 250);
            }"""
            
    if target2 in js:
        js = js.replace(target2, replacement2)
        print("Patched setTimeout pollScanStatus")
        
    with open('app/static/js/scanner.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched scanner.js with queue indicator logic")
else:
    print("Target not found in scanner.js")
