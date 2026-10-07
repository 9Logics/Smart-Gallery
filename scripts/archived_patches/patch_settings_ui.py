import re
path = 'app/templates/partials/views/view-settings.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

update_card = """                    <!-- Card 5: App Updates -->
                    <div class="settings-card">
                        <h3>App Updates</h3>
                        <p class="settings-desc">Keep your app up to date with the latest features from GitHub.</p>
                        
                        <div class="settings-item">
                            <div class="settings-item-info">
                                <span class="settings-item-header">Check for Updates</span>
                                <span class="settings-item-desc">Automatically download and apply the latest update.</span>
                            </div>
                            <div class="settings-action">
                                <button id="btn-update-app" class="btn btn-secondary">
                                    <i data-lucide="refresh-cw"></i> Update Now
                                </button>
                            </div>
                        </div>
                    </div>
"""

# Insert it before the closing tags of the settings view
if "<!-- Card 5: App Updates -->" not in html:
    html = html.replace("                    </div>\n                </div>", update_card + "\n                    </div>\n                </div>")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Added App Updates card to settings.")
else:
    print("Card already exists.")
