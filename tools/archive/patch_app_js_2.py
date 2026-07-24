import re

with open('static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
        if (data.success && data.new_path) {
            alert("File was found at a new location! Updating gallery link and reloading...");
            closeLightbox();
            loadStaticData();
            setTimeout(() => openLightbox(data.new_path), 500);
        } else {
            // Show Retarget Modal
            const modalHTML = `
                <div id="retarget-modal-overlay" class="retarget-modal-overlay visible">
                    <div class="retarget-modal-content">
                        <div class="retarget-modal-header">
                            <i data-lucide="file-question" style="color: var(--accent-color);"></i>
                            File Not Found
                        </div>
                        <div class="retarget-modal-body">
                            The file could not be found at its original location or inside any tracked directories.
                        </div>
                        <div class="retarget-input-group">
                            <label>Retarget File (Absolute Folder Path)</label>
                            <input type="text" id="retarget-dir-input" placeholder="e.g. D:\\My New Folder">
                        </div>
                        <div class="retarget-modal-actions">
                            <button class="btn-cancel-retarget" id="retarget-cancel-btn">Cancel</button>
                            <button class="btn-delete-record" id="retarget-delete-btn">
                                <i data-lucide="trash-2" style="width:14px; height:14px;"></i> Remove from Gallery
                            </button>
                            <button class="btn-retarget" id="retarget-search-btn">
                                <i data-lucide="search" style="width:14px; height:14px;"></i> Search Directory
                            </button>
                        </div>
                    </div>
                </div>
            `;
            const wrapper = document.createElement('div');
            wrapper.innerHTML = modalHTML;
            const overlay = wrapper.firstElementChild;
            document.body.appendChild(overlay);
            lucide.createIcons();
            
            const cleanupModal = () => {
                overlay.classList.remove('visible');
                setTimeout(() => document.body.removeChild(overlay), 300);
            };
            
            document.getElementById('retarget-cancel-btn').onclick = cleanupModal;
            
            document.getElementById('retarget-delete-btn').onclick = () => {
                cleanupModal();
                fetch('/api/photo/delete_record', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path: photoPath })
                }).then(() => {
                    closeLightbox();
                    loadPhotos(); // reload grid
                });
            };
            
            document.getElementById('retarget-search-btn').onclick = () => {
                const searchDir = document.getElementById('retarget-dir-input').value.trim();
                if (!searchDir) {
                    alert('Please enter a directory path to search.');
                    return;
                }
                
                const btn = document.getElementById('retarget-search-btn');
                btn.disabled = true;
                btn.innerHTML = `<i data-lucide="loader-2" class="spin" style="width:14px; height:14px;"></i> Searching...`;
                lucide.createIcons();
                
                fetch('/api/photo/find_missing', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path: photoPath, search_dir: searchDir })
                })
                .then(r => r.json())
                .then(rData => {
                    cleanupModal();
                    if (rData.success && rData.new_path) {
                        alert("File found! Updating gallery...");
                        closeLightbox();
                        loadStaticData();
                        setTimeout(() => openLightbox(rData.new_path), 500);
                    } else {
                        alert("File was not found in that directory.");
                    }
                })
                .catch(() => {
                    alert("Error searching directory.");
                    cleanupModal();
                });
            };
        }
"""

old_logic_pattern = re.compile(r"        if \(data\.success && data\.new_path\) \{.*?\}\);\n            \}\n        \}", re.DOTALL)
content = old_logic_pattern.sub(new_logic.strip(), content)

with open('static/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('app.js patched.')
