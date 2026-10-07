with open("app/static/js/core.js", "a") as f:
    f.write("""

// Archive Category Navigation
document.addEventListener('DOMContentLoaded', () => {
    const archiveNav = document.getElementById('archive-categories-nav');
    if (!archiveNav) return;
    
    archiveNav.addEventListener('click', (e) => {
        const btn = e.target.closest('.category-btn');
        if (!btn) return;
        
        // Update active class
        archiveNav.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update global filter state
        window.currentArchiveCategory = btn.dataset.category;
        
        // Reload photos with new filter
        if (typeof window.switchView === 'function') {
            window.switchView('archive');
        }
    });
});
""")
print("Added event listeners for archive categories.")
