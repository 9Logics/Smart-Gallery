import codecs

new_logic = """
// ==========================================
// Lightbox Refresh Button Wiring
// ==========================================
const btnRefreshPhoto = document.getElementById('lightbox-refresh-btn');
if (btnRefreshPhoto) {
    btnRefreshPhoto.addEventListener('click', () => {
        if (!state.currentLightboxPhoto) return;
        
        // Spin the icon
        const icon = btnRefreshPhoto.querySelector('i');
        if (icon) {
            icon.style.transition = 'transform 1s linear';
            icon.style.transform = 'rotate(360deg)';
        }
        
        fetch('/api/photo/refresh', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: state.currentLightboxPhoto })
        })
        .then(res => {
            if (res.status === 404) {
                return res.json().then(data => {
                    if (data.error === "file_missing") {
                        handleMissingPhoto(state.currentLightboxPhoto);
                        return null; // Stop propagation
                    }
                    throw new Error("File not found");
                });
            }
            return res.json();
        })
        .then(data => {
            if (!data) return; // Handled missing
            
            if (icon) {
                icon.style.transform = '';
            }
            if (data.success) {
                if (icon) {
                    const originalLucide = icon.getAttribute('data-lucide');
                    icon.setAttribute('data-lucide', 'check');
                    icon.style.color = '#10b981';
                    lucide.createIcons();
                    setTimeout(() => {
                        icon.setAttribute('data-lucide', originalLucide);
                        icon.style.color = '';
                        lucide.createIcons();
                        const path = state.currentLightboxPhoto;
                        closeLightbox();
                        setTimeout(() => openLightbox(path), 300);
                    }, 1500);
                } else {
                    const path = state.currentLightboxPhoto;
                    closeLightbox();
                    setTimeout(() => openLightbox(path), 300);
                }
            } else {
                alert("Failed to refresh photo: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            if (icon) icon.style.transform = '';
            alert("Error refreshing photo.");
        });
    });
}

function handleMissingPhoto(photoPath) {
    // Show a loading throbber/bar at the bottom of the screen
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'missing-file-loader';
    loadingDiv.style.position = 'fixed';
    loadingDiv.style.bottom = '20px';
    loadingDiv.style.left = '50%';
    loadingDiv.style.transform = 'translateX(-50%)';
    loadingDiv.style.background = 'var(--bg-card)';
    loadingDiv.style.padding = '10px 20px';
    loadingDiv.style.borderRadius = '8px';
    loadingDiv.style.boxShadow = '0 4px 12px rgba(0,0,0,0.5)';
    loadingDiv.style.zIndex = '9999';
    loadingDiv.style.display = 'flex';
    loadingDiv.style.alignItems = 'center';
    loadingDiv.style.gap = '10px';
    loadingDiv.style.fontSize = '14px';
    loadingDiv.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Looking for missing file...`;
    document.body.appendChild(loadingDiv);
    lucide.createIcons();
    
    fetch('/api/photo/find_missing', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ path: photoPath })
    })
    .then(res => res.json())
    .then(data => {
        document.body.removeChild(loadingDiv);
        if (data.success && data.new_path) {
            alert("File was found at a new location! Updating gallery link and reloading...");
            closeLightbox();
            loadStaticData();
            setTimeout(() => openLightbox(data.new_path), 500);
        } else {
            const confirmDelete = confirm("File has been deleted (not found). Would you like to remove it from the gallery?");
            if (confirmDelete) {
                fetch('/api/photo/delete_record', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ path: photoPath })
                }).then(() => {
                    closeLightbox();
                    loadStaticData();
                });
            } else {
                if (document.getElementById('lightbox-refresh-btn')) {
                    document.getElementById('lightbox-refresh-btn').querySelector('i').style.transform = '';
                }
            }
        }
    })
    .catch(err => {
        document.body.removeChild(loadingDiv);
        alert("Error while searching for missing file.");
    });
}
"""

with codecs.open('static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.strip() == "// Lightbox Refresh Button Wiring":
        start_idx = i - 1
    elif line.strip() == "// Deep Scan / Look for More Button" and start_idx != -1:
        end_idx = i - 1
        break

if start_idx != -1 and end_idx != -1:
    with codecs.open('static/app.js', 'w', encoding='utf-8') as f:
        f.writelines(lines[:start_idx])
        f.write(new_logic + "\n")
        f.writelines(lines[end_idx:])
    print("Successfully patched app.js")
else:
    print(f"Failed: start_idx={start_idx}, end_idx={end_idx}")
