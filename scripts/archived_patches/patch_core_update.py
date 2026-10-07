import os
path = 'app/static/js/core.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

update_logic = """
// App Updates
const btnUpdateApp = document.getElementById('btn-update-app');
if (btnUpdateApp) {
    btnUpdateApp.addEventListener('click', async () => {
        const originalText = btnUpdateApp.innerHTML;
        btnUpdateApp.innerHTML = '<i data-lucide="loader" class="spin"></i> Updating...';
        btnUpdateApp.disabled = true;
        lucide.createIcons();
        
        try {
            const res = await fetch('/api/system/update', { method: 'POST' });
            const data = await res.json();
            
            if (res.ok) {
                alert('Update Successful: ' + data.message);
                if (data.restart_required) {
                    setTimeout(() => window.close(), 1500); // Close the webview
                }
            } else {
                alert('Update Failed: ' + (data.error || 'Unknown error'));
            }
        } catch (e) {
            alert('Update Failed: ' + e.message);
        } finally {
            btnUpdateApp.innerHTML = originalText;
            btnUpdateApp.disabled = false;
            lucide.createIcons();
        }
    });
}
"""

if "btnUpdateApp" not in code:
    code += update_logic
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added update logic to core.js")
else:
    print("Logic already exists.")
