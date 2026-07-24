import codecs

js_code = """
// ==========================================
// Deep Scan / Look for More Button
// ==========================================
const btnDeepScan = document.getElementById('deep-scan-faces-btn');
if (btnDeepScan) {
    btnDeepScan.addEventListener('click', () => {
        if (!state.currentLightboxPhoto) return;
        
        btnDeepScan.disabled = true;
        const origHtml = btnDeepScan.innerHTML;
        btnDeepScan.innerHTML = `<i data-lucide="loader-2" style="width:14px; height:14px;" class="spin"></i> Scanning...`;
        lucide.createIcons();
        
        fetch('/api/photo/deep-scan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ path: state.currentLightboxPhoto })
        })
        .then(res => res.json())
        .then(data => {
            btnDeepScan.disabled = false;
            btnDeepScan.innerHTML = origHtml;
            lucide.createIcons();
            
            if (data.success) {
                if (data.new_faces_count > 0) {
                    alert(`Found ${data.new_faces_count} new face(s)!`);
                    // Refresh lightbox to show new faces
                    const path = state.currentLightboxPhoto;
                    closeLightbox();
                    setTimeout(() => openLightbox(path), 300);
                } else {
                    alert("No additional faces found even with high sensitivity.");
                }
            } else {
                alert("Failed to deep scan: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            btnDeepScan.disabled = false;
            btnDeepScan.innerHTML = origHtml;
            lucide.createIcons();
            alert("Error running deep scan.");
        });
    });
}
"""

with codecs.open('static/app.js', 'a', encoding='utf-8') as f:
    f.write('\n' + js_code)
