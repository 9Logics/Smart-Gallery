import re

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = """                            <div class="slideout-stats">
                                <span id="slideout-count" class="slideout-count">0/0</span>
                                <span id="slideout-pct" class="slideout-pct">(0%)</span>
                            </div>
                            <button class="slideout-cancel-btn" onclick="cancelScan()">Cancel</button>"""

replacement = """                            <div class="slideout-stats">
                                <span id="slideout-count" class="slideout-count">0/0</span>
                                <span id="slideout-pct" class="slideout-pct">(0%)</span>
                            </div>
                            <!-- NEW: Queue indicator -->
                            <div id="slideout-queue-indicator" class="hidden" style="display: flex; align-items: center; gap: 4px; padding: 2px 6px; background: rgba(255,255,255,0.1); border-radius: 4px; margin-right: 8px; font-size: 11px; font-weight: 500; color: rgba(255,255,255,0.7);">
                                <i data-lucide="list-video" style="width: 12px; height: 12px;"></i>
                                <span id="slideout-queue-count">0 in queue</span>
                            </div>
                            <button class="slideout-cancel-btn" onclick="cancelScan()">Cancel</button>"""

if target in html:
    html = html.replace(target, replacement)
    with open('app/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Patched index.html with slideout queue indicator")
else:
    print("Target not found in index.html")
