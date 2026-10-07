with open("app/static/js/core.js", "r", encoding="utf-8") as f:
    content = f.read()

# Find the last two instances of "// Archive Category Navigation"
parts = content.split("// Archive Category Navigation")
if len(parts) > 2:
    # Keep up to the first one, but replace with a single clean one
    clean = parts[0] + """// Archive Category Navigation
document.addEventListener('DOMContentLoaded', () => {
    const archiveNav = document.getElementById('archive-categories-nav');
    if (!archiveNav) return;
    
    archiveNav.addEventListener('click', (e) => {
        const btn = e.target.closest('.category-btn');
        if (!btn) return;
        
        // Update styling
        archiveNav.querySelectorAll('.category-btn').forEach(b => {
            b.classList.remove('active', 'btn-primary');
            b.classList.add('btn-secondary');
            b.style.background = '';
            b.style.color = '';
        });
        btn.classList.add('active', 'btn-primary');
        btn.classList.remove('btn-secondary');
        
        // Update global filter state
        window.currentArchiveCategory = btn.dataset.category;
        
        // Reload photos with new filter
        if (typeof window.switchView === 'function') {
            window.switchView('archive');
        }
    });
});
"""
    with open("app/static/js/core.js", "w", encoding="utf-8") as f:
        f.write(clean)
    print("Fixed core.js bottom.")
else:
    print("Not enough parts.")
