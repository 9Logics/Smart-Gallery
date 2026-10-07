import re

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

target = """        try {
            const response = await fetch('/api/data/export?' + params.toString(), { method: 'GET' });
            if (!response.ok) throw new Error('Network response was not ok');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            const now = new Date();
            const dateStr = now.getFullYear() + '-' + 
                            String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(now.getDate()).padStart(2, '0') + ' ' + 
                            String(now.getHours()).padStart(2, '0') + '-' + 
                            String(now.getMinutes()).padStart(2, '0');
            a.download = `gallery backup ${dateStr}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            hideDataModal();
        } catch (err) {"""

replacement = """        const paramsObj = {
            photos: document.getElementById('exp-photos').checked,
            albums: document.getElementById('exp-albums').checked,
            faces: document.getElementById('exp-faces').checked,
            face_imgs: document.getElementById('exp-face-imgs').checked,
            thumbs: document.getElementById('exp-thumbs').checked,
            ai: document.getElementById('exp-ai').checked
        };
        
        try {
            if (window.pywebview && window.pywebview.api && window.pywebview.api.export_backup) {
                const res = await window.pywebview.api.export_backup(paramsObj);
                hideDataModal();
                if (res.cancelled) return; // user cancelled save dialog
                if (res.error) throw new Error(res.error);
                alert("Backup exported successfully to: " + res.path);
                return;
            }
        
            const response = await fetch('/api/data/export?' + params.toString(), { method: 'GET' });
            if (!response.ok) throw new Error('Network response was not ok');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            const now = new Date();
            const dateStr = now.getFullYear() + '-' + 
                            String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(now.getDate()).padStart(2, '0') + ' ' + 
                            String(now.getHours()).padStart(2, '0') + '-' + 
                            String(now.getMinutes()).padStart(2, '0');
            a.download = `gallery backup ${dateStr}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            hideDataModal();
        } catch (err) {"""

if target in js:
    js = js.replace(target, replacement)
    with open('app/static/js/core.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Patched core.js")
else:
    print("Target not found in core.js")
