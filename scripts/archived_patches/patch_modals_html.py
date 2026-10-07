import re

html_to_inject = """
    <!-- Custom In-App Alert/Confirm Modals -->
    <div id="app-alert-modal" class="retarget-modal-overlay hidden" style="z-index: 10001; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px); background: rgba(0,0,0,0.6);">
        <div class="retarget-modal-content" style="max-width: 400px; padding: 25px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
            <h3 id="app-alert-title" style="margin-top: 0; color: var(--text-color); font-size: 18px; font-weight: 600;">Message</h3>
            <p id="app-alert-msg" style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px; word-wrap: break-word;"></p>
            <div style="display: flex; justify-content: flex-end;">
                <button id="app-alert-btn" class="btn btn-primary">OK</button>
            </div>
        </div>
    </div>

    <div id="app-confirm-modal" class="retarget-modal-overlay hidden" style="z-index: 10001; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px); background: rgba(0,0,0,0.6);">
        <div class="retarget-modal-content" style="max-width: 400px; padding: 25px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
            <h3 id="app-confirm-title" style="margin-top: 0; color: var(--text-color); font-size: 18px; font-weight: 600;">Confirm</h3>
            <p id="app-confirm-msg" style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px; word-wrap: break-word;"></p>
            <div style="display: flex; justify-content: flex-end; gap: 8px;">
                <button id="app-confirm-cancel-btn" class="btn btn-secondary">Cancel</button>
                <button id="app-confirm-ok-btn" class="btn btn-primary">OK</button>
            </div>
        </div>
    </div>
"""

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = "    <!-- Lightbox/Preview Modal -->"

if html_to_inject not in html:
    html = html.replace(target, html_to_inject + "\n" + target)
    with open('app/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Injected modals into index.html")
else:
    print("Modals already injected")
