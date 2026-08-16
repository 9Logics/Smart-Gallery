// Script to append idle logic
import fs from 'fs';
const filePath = 'static/js/views/memories.js';
let text = fs.readFileSync(filePath, 'utf8');

const idleLogic = \

// ==========================================
// Dashboard Idle Hero Scanner
// ==========================================
let heroIdleTimer = null;
let heroIdleActive = false;

function resetHeroIdleTimer() {
    if (heroIdleTimer) clearTimeout(heroIdleTimer);
    
    // Only run idle scanning if we are on the memories view
    if (document.getElementById('memories-view') && !document.getElementById('memories-view').classList.contains('hidden')) {
        heroIdleTimer = setTimeout(() => {
            heroIdleActive = true;
            // Silent background scan when user is idle for 30 seconds
            fetch('/api/memories/hero/scan_more', { method: 'POST' });
            
            // Re-trigger every 30s of deep idle
            heroIdleTimer = setInterval(() => {
                fetch('/api/memories/hero/scan_more', { method: 'POST' });
            }, 30000);
            
        }, 30000);
    }
}

function handleDashboardActivity() {
    if (heroIdleActive) {
        heroIdleActive = false;
        if (heroIdleTimer) clearInterval(heroIdleTimer);
    }
    resetHeroIdleTimer();
}

window.addEventListener('mousemove', handleDashboardActivity, {passive: true});
window.addEventListener('keydown', handleDashboardActivity, {passive: true});
window.addEventListener('scroll', handleDashboardActivity, {passive: true});

// Make sure to clean up event listeners if needed, though they can persist globally 
// as long as they check for memories-view
\;

text += idleLogic;
fs.writeFileSync(filePath, text);
