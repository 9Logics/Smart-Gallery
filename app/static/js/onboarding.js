document.addEventListener('DOMContentLoaded', () => {
    // Only run if onboarding overlay exists
    const overlay = document.getElementById('onboarding-overlay');
    if (!overlay) return;

    // Force background view to home (memories)
    setTimeout(() => {
        if (typeof switchView === 'function') {
            switchView('memories');
        }
    }, 100);

    // Start Page 1 Animations
    setTimeout(() => {
        const iconContainer = document.querySelector('.app-icon-container');
        const nameContainer = document.getElementById('splash-app-name');
        const actions = document.getElementById('splash-actions');

        if (iconContainer) iconContainer.classList.add('float-up');
        
        setTimeout(() => {
            if (nameContainer) {
                nameContainer.classList.remove('hidden');
                nameContainer.classList.add('reveal');
            }
            if (actions) {
                actions.classList.remove('hidden');
                actions.classList.add('reveal');
            }
        }, 500); // Wait half second after floating up to reveal text

    }, 3000); // 3 second delay as requested
});

function obGoToPage(pageNum) {
    // Hide all pages
    document.querySelectorAll('.onboarding-page').forEach(p => {
        p.classList.remove('active');
    });
    
    // Show target page
    const target = document.getElementById(`ob-page-${pageNum}`);
    if (target) {
        target.classList.add('active');
    }

    // Update progress bar
    document.querySelectorAll('.progress-segment').forEach((seg, idx) => {
        if (idx < pageNum) {
            seg.classList.add('active');
        } else {
            seg.classList.remove('active');
        }
    });
}


let obValidationTimeout = null;

function obCheckFolderInput() {
    const input = document.getElementById('ob-folder-input');
    const nextBtn = document.getElementById('ob-next-btn');
    const errorMsg = document.getElementById('ob-error-msg');
    const path = input.value.trim();
    
    // Hide button and error by default
    nextBtn.classList.add('hidden');
    
    
    errorMsg.style.display = 'none';
    
    if (path.length === 0) return;
    
    if (obValidationTimeout) clearTimeout(obValidationTimeout);
    
    obValidationTimeout = setTimeout(() => {
        fetch('/api/settings/validate-folder', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ folder: path })
        })
        .then(res => res.json())
        .then(data => {
            if (data.valid) {
                errorMsg.style.display = 'none';
                nextBtn.classList.remove('hidden');
                
                
            } else {
                errorMsg.textContent = data.error;
                errorMsg.style.display = 'block';
            }
        })
        .catch(err => console.error(err));
    }, 500); // 500ms debounce
}

function obSelectFolder() {
    fetch('/api/settings/browse_directory')
        .then(res => res.json())
        .then(data => {
            if (data.path) {
                const input = document.getElementById('ob-folder-input');
                input.value = data.path;
                obCheckFolderInput();
            }
        })
        .catch(err => console.error(err));
}

function obFinishSetup() {
    const input = document.getElementById('ob-folder-input');
    const path = input.value;
    
    if (!path) {
        appAlert("Please enter a folder first.");
        return;
    }

    // Call API to set directory and finish setup
    fetch('/api/settings/scan-folder', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ folder: path })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success || !data.error) {
            // Trigger scan
            fetch('/api/scan', { method: 'POST' });
            
            // Fade out overlay and remove
            const overlay = document.getElementById('onboarding-overlay');
            overlay.style.transition = "opacity 0.8s ease";
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.remove();
                // Optionally reload the page to initialize gallery properly
                window.location.reload();
            }, 800);
        } else {
            appAlert(data.error || "Failed to save directory.");
        }
    })
    .catch(err => {
        // Assume success if no JSON error payload
        console.error(err);
        fetch('/api/scan', { method: 'POST' });
        const overlay = document.getElementById('onboarding-overlay');
        overlay.style.transition = "opacity 0.8s ease";
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.remove();
            window.location.reload();
        }, 800);
    });
}
