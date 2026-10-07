import os
import re

js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# I will replace the nextRecapSlide and prevRecapSlide functions with new ones that trigger a transition layer
old_nav = '''function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        recapCurrentSlide++;
        showRecapSlide(recapCurrentSlide);
    } else {
        closeRecapPlayer();
    }
}

function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        recapCurrentSlide--;
        showRecapSlide(recapCurrentSlide);
    }
}'''

new_nav = '''let isTransitioning = false;

function playSlideTransition(callback) {
    if (isTransitioning) return;
    isTransitioning = true;
    
    const layer = document.getElementById('recap-slide-transition');
    layer.style.display = 'block';
    layer.innerHTML = '';
    
    const types = ['wipe-right', 'wipe-up', 'flash', 'shutter'];
    const type = types[Math.floor(Math.random() * types.length)];
    
    if (type === 'wipe-right' || type === 'wipe-up') {
        const wipe = document.createElement('div');
        wipe.style.position = 'absolute';
        wipe.style.background = 'white';
        
        if (type === 'wipe-right') {
            wipe.style.top = '0'; wipe.style.bottom = '0'; wipe.style.width = '0'; wipe.style.left = '0';
            wipe.style.transition = 'width 0.3s cubic-bezier(0.8, 0, 0.2, 1)';
        } else {
            wipe.style.left = '0'; wipe.style.right = '0'; wipe.style.height = '0'; wipe.style.bottom = '0';
            wipe.style.transition = 'height 0.3s cubic-bezier(0.8, 0, 0.2, 1)';
        }
        
        layer.appendChild(wipe);
        
        // Trigger In
        requestAnimationFrame(() => {
            if (type === 'wipe-right') wipe.style.width = '100vw';
            if (type === 'wipe-up') wipe.style.height = '100vh';
        });
        
        setTimeout(() => {
            callback(); // Swap slide behind the wipe
            
            // Trigger Out
            if (type === 'wipe-right') {
                wipe.style.left = 'auto'; wipe.style.right = '0'; wipe.style.width = '0';
            } else {
                wipe.style.bottom = 'auto'; wipe.style.top = '0'; wipe.style.height = '0';
            }
            
            setTimeout(() => {
                layer.style.display = 'none';
                isTransitioning = false;
            }, 300);
        }, 300);
    } 
    else if (type === 'flash') {
        layer.style.background = 'white';
        layer.style.opacity = '0';
        layer.style.transition = 'opacity 0.15s ease-out';
        
        requestAnimationFrame(() => {
            layer.style.opacity = '1';
        });
        
        setTimeout(() => {
            callback();
            layer.style.opacity = '0';
            setTimeout(() => {
                layer.style.display = 'none';
                isTransitioning = false;
            }, 150);
        }, 150);
    }
    else if (type === 'shutter') {
        const top = document.createElement('div');
        const bottom = document.createElement('div');
        top.style.position = 'absolute'; bottom.style.position = 'absolute';
        top.style.left = '0'; top.style.right = '0'; top.style.height = '0'; top.style.background = '#111';
        bottom.style.left = '0'; bottom.style.right = '0'; bottom.style.height = '0'; bottom.style.background = '#111';
        top.style.top = '0'; bottom.style.bottom = '0';
        top.style.transition = 'height 0.2s cubic-bezier(0.8, 0, 0.2, 1)';
        bottom.style.transition = 'height 0.2s cubic-bezier(0.8, 0, 0.2, 1)';
        
        layer.appendChild(top);
        layer.appendChild(bottom);
        
        requestAnimationFrame(() => {
            top.style.height = '50vh';
            bottom.style.height = '50vh';
        });
        
        setTimeout(() => {
            callback();
            top.style.height = '0';
            bottom.style.height = '0';
            setTimeout(() => {
                layer.style.display = 'none';
                isTransitioning = false;
            }, 200);
        }, 250);
    }
}

function nextRecapSlide() {
    if (recapCurrentSlide < recapSlides.length - 1) {
        playSlideTransition(() => {
            recapCurrentSlide++;
            showRecapSlide(recapCurrentSlide);
        });
    } else {
        closeRecapPlayer();
    }
}

function prevRecapSlide() {
    if (recapCurrentSlide > 0) {
        playSlideTransition(() => {
            recapCurrentSlide--;
            showRecapSlide(recapCurrentSlide);
        });
    }
}'''

js = js.replace(old_nav, new_nav)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Injected random slide transitions!")
