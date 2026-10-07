import re

js_to_append = """
// --- Custom App Alert & Confirm ---
window.appAlert = function(message, title = "Message") {
    return new Promise(resolve => {
        const modal = document.getElementById('app-alert-modal');
        const titleEl = document.getElementById('app-alert-title');
        const msgEl = document.getElementById('app-alert-msg');
        const btn = document.getElementById('app-alert-btn');
        
        if (!modal) {
            alert(message);
            resolve();
            return;
        }
        
        titleEl.textContent = title;
        msgEl.textContent = message;
        modal.classList.remove('hidden');
        
        const cleanup = () => {
            modal.classList.add('hidden');
            btn.removeEventListener('click', onClick);
            resolve();
        };
        
        const onClick = () => cleanup();
        btn.addEventListener('click', onClick);
    });
};

window.appConfirm = function(message, title = "Confirm") {
    return new Promise(resolve => {
        const modal = document.getElementById('app-confirm-modal');
        const titleEl = document.getElementById('app-confirm-title');
        const msgEl = document.getElementById('app-confirm-msg');
        const okBtn = document.getElementById('app-confirm-ok-btn');
        const cancelBtn = document.getElementById('app-confirm-cancel-btn');
        
        if (!modal) {
            resolve(confirm(message));
            return;
        }
        
        titleEl.textContent = title;
        msgEl.textContent = message;
        modal.classList.remove('hidden');
        
        const cleanup = (result) => {
            modal.classList.add('hidden');
            okBtn.removeEventListener('click', onOk);
            cancelBtn.removeEventListener('click', onCancel);
            resolve(result);
        };
        
        const onOk = () => cleanup(true);
        const onCancel = () => cleanup(false);
        
        okBtn.addEventListener('click', onOk);
        cancelBtn.addEventListener('click', onCancel);
    });
};
"""

with open('app/static/js/core.js', 'r', encoding='utf-8') as f:
    js = f.read()

if "window.appAlert" not in js:
    with open('app/static/js/core.js', 'a', encoding='utf-8') as f:
        f.write("\n" + js_to_append)
    print("Appended custom modal JS to core.js")
else:
    print("Custom modal JS already in core.js")
