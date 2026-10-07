import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

target1 = """if (btnImportCache) {
    btnImportCache.addEventListener('click', () => {
        importCacheInput.click();
    });
}"""

replacement1 = """if (btnImportCache) {
    btnImportCache.addEventListener('click', async () => {
        if (window.pywebview && window.pywebview.api && window.pywebview.api.select_import_file) {
            const res = await window.pywebview.api.select_import_file();
            if (res && res.path) {
                window.pendingImportFilePath = res.path;
                document.getElementById('import-options-modal').classList.remove('hidden'); 
                setTimeout(()=>document.getElementById('import-options-modal').classList.add('visible'), 10);
            }
        } else {
            importCacheInput.click();
        }
    });
}"""

target2 = """const confirmImportBtn = document.getElementById('confirm-import-btn');
if (confirmImportBtn) {
    confirmImportBtn.addEventListener('click', async () => {
        document.getElementById('import-options-modal').classList.remove('visible'); setTimeout(()=>document.getElementById('import-options-modal').classList.add('hidden'), 300);
        if (!pendingImportFile) return;
        
        showDataModal("Importing Backup...", "Uploading and merging selected data. Do not close the window!");
        
        const formData = new FormData();
        formData.append('file', pendingImportFile);
        formData.append('photos', document.getElementById('imp-photos').checked);
        formData.append('albums', document.getElementById('imp-albums').checked);
        formData.append('faces', document.getElementById('imp-faces').checked);
        formData.append('face_imgs', document.getElementById('imp-face-imgs').checked);
        formData.append('thumbs', document.getElementById('imp-thumbs').checked);
        formData.append('ai', document.getElementById('imp-ai').checked);
        
        try {
            const response = await fetch('/api/data/import', {
                method: 'POST',
                body: formData
            });"""

replacement2 = """const confirmImportBtn = document.getElementById('confirm-import-btn');
if (confirmImportBtn) {
    confirmImportBtn.addEventListener('click', async () => {
        document.getElementById('import-options-modal').classList.remove('visible'); setTimeout(()=>document.getElementById('import-options-modal').classList.add('hidden'), 300);
        
        if (window.pywebview && window.pywebview.api && window.pywebview.api.import_backup) {
            if (!window.pendingImportFilePath) return;
            showDataModal("Importing Backup...", "Extracting and merging selected data. Do not close the window!");
            
            const paramsObj = {
                path: window.pendingImportFilePath,
                photos: document.getElementById('imp-photos').checked,
                albums: document.getElementById('imp-albums').checked,
                faces: document.getElementById('imp-faces').checked,
                face_imgs: document.getElementById('imp-face-imgs').checked,
                thumbs: document.getElementById('imp-thumbs').checked,
                ai: document.getElementById('imp-ai').checked
            };
            
            try {
                const res = await window.pywebview.api.import_backup(paramsObj);
                if (res.error) throw new Error(res.error);
                if (res.success) {
                    dataOpTitle.textContent = "Success!";
                    dataOpDesc.textContent = "Data imported successfully. Reloading app...";
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    hideDataModal();
                    alert(res.error || "Import failed");
                }
            } catch (err) {
                hideDataModal();
                alert('Import failed: ' + err.message);
            }
            return;
        }

        if (!pendingImportFile) return;
        
        showDataModal("Importing Backup...", "Uploading and merging selected data. Do not close the window!");
        
        const formData = new FormData();
        formData.append('file', pendingImportFile);
        formData.append('photos', document.getElementById('imp-photos').checked);
        formData.append('albums', document.getElementById('imp-albums').checked);
        formData.append('faces', document.getElementById('imp-faces').checked);
        formData.append('face_imgs', document.getElementById('imp-face-imgs').checked);
        formData.append('thumbs', document.getElementById('imp-thumbs').checked);
        formData.append('ai', document.getElementById('imp-ai').checked);
        
        try {
            const response = await fetch('/api/data/import', {
                method: 'POST',
                body: formData
            });"""

if target1 in js and target2 in js:
    js = js.replace(target1, replacement1)
    js = js.replace(target2, replacement2)
    with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched core.js for Native Import")
else:
    print("Target not found in core.js")
