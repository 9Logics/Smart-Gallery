with open('static/app.js', 'a', encoding='utf-8') as f:
    f.write('''\n
// ==========================================
// File Path Editor (Retargeting)
// ==========================================
const btnEditPath = document.getElementById('edit-path-btn');
const pathEditorContainer = document.getElementById('path-editor-container');
const editPathInput = document.getElementById('edit-path-input');
const btnSavePath = document.getElementById('save-path-btn');
const btnCancelPath = document.getElementById('cancel-path-btn');

if (btnEditPath) {
    btnEditPath.addEventListener('click', () => {
        if (!state.currentLightboxPhoto) return;
        pathEditorContainer.classList.remove('hidden');
        editPathInput.value = state.currentLightboxPhoto;
        editPathInput.focus();
    });
}

if (btnCancelPath) {
    btnCancelPath.addEventListener('click', () => {
        pathEditorContainer.classList.add('hidden');
    });
}

if (btnSavePath) {
    btnSavePath.addEventListener('click', () => {
        const newPath = editPathInput.value.trim();
        if (!newPath) return;
        if (newPath === state.currentLightboxPhoto) {
            pathEditorContainer.classList.add('hidden');
            return;
        }
        
        btnSavePath.disabled = true;
        btnSavePath.innerText = 'Saving...';
        
        fetch('/api/photo/find_missing', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: state.currentLightboxPhoto, search_dir: newPath })
        })
        .then(res => res.json())
        .then(data => {
            btnSavePath.disabled = false;
            btnSavePath.innerText = 'Retarget';
            
            if (data.success && data.new_path) {
                pathEditorContainer.classList.add('hidden');
                alert("File retargeted successfully! Updating gallery...");
                closeLightbox();
                loadStaticData();
                setTimeout(() => openLightbox(data.new_path), 500);
            } else {
                alert("Could not find or verify the file at that exact path.");
            }
        })
        .catch(err => {
            btnSavePath.disabled = false;
            btnSavePath.innerText = 'Retarget';
            alert("Error while retargeting file.");
        });
    });
}
''')
print('Path Editor JS appended.')
