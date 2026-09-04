// Select Modernizer script
function modernizeSelect(selectElement) {
    if (selectElement.dataset.modernized === 'true') {
        return;
    }
    
    selectElement.style.display = 'none';
    selectElement.dataset.modernized = 'true';
    
    const wrapper = document.createElement('div');
    wrapper.className = 'custom-select-wrapper';
    
    if (selectElement.style.width) wrapper.style.width = selectElement.style.width;
    
    const customSelect = document.createElement('div');
    customSelect.className = 'custom-select';
    
    const trigger = document.createElement('div');
    trigger.className = 'custom-select-trigger';
    
    const textSpan = document.createElement('span');
    
    const arrowSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    arrowSvg.setAttribute('class', 'arrow');
    arrowSvg.setAttribute('viewBox', '0 0 24 24');
    const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    polyline.setAttribute('points', '6 9 12 15 18 9');
    arrowSvg.appendChild(polyline);
    
    trigger.appendChild(textSpan);
    trigger.appendChild(arrowSvg);
    
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'custom-select-options';
    
    // We append to document.body instead of customSelect to completely bypass ALL z-index/clipping issues!
    document.body.appendChild(optionsContainer);
    
    customSelect.appendChild(trigger);
    wrapper.appendChild(customSelect);
    
    selectElement.parentNode.insertBefore(wrapper, selectElement.nextSibling);

    const rebuildOptions = () => {
        optionsContainer.innerHTML = '';
        textSpan.textContent = selectElement.options[selectElement.selectedIndex]?.text || '';
        
        Array.from(selectElement.options).forEach((opt, index) => {
            if (!opt.value && !opt.text.trim()) return; // Skip empty options
            
            const optionDiv = document.createElement('div');
            optionDiv.className = 'custom-option';
            optionDiv.textContent = opt.text;
            if (index === selectElement.selectedIndex) {
                optionDiv.classList.add('selected');
            }
            
            optionDiv.addEventListener('click', (e) => {
                e.stopPropagation();
                selectElement.selectedIndex = index;
                textSpan.textContent = opt.text;
                
                optionsContainer.querySelectorAll('.custom-option').forEach(el => el.classList.remove('selected'));
                optionDiv.classList.add('selected');
                
                customSelect.classList.remove('open');
                optionsContainer.classList.remove('open');
                selectElement.dispatchEvent(new Event('change', { bubbles: true }));
            });
            
            optionsContainer.appendChild(optionDiv);
        });
    };
    
    rebuildOptions();
    
    const optionObserver = new MutationObserver(rebuildOptions);
    optionObserver.observe(selectElement, { childList: true, subtree: true, characterData: true });
    
    selectElement.addEventListener('change', () => {
        textSpan.textContent = selectElement.options[selectElement.selectedIndex]?.text || '';
        optionsContainer.querySelectorAll('.custom-option').forEach((el, i) => {
            el.classList.toggle('selected', i === selectElement.selectedIndex);
        });
    });
    
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        
        const isOpen = customSelect.classList.contains('open');
        
        // Close all others
        document.querySelectorAll('.custom-select.open').forEach(el => el.classList.remove('open'));
        document.querySelectorAll('.custom-select-options.open').forEach(el => el.classList.remove('open'));
        
        if (!isOpen) {
            customSelect.classList.add('open');
            optionsContainer.classList.add('open');
            
            // Calculate absolute position
            const rect = trigger.getBoundingClientRect();
            optionsContainer.style.top = (rect.bottom + window.scrollY + 4) + 'px';
            optionsContainer.style.left = (rect.left + window.scrollX) + 'px';
            optionsContainer.style.width = rect.width + 'px';
        }
    });
    
    // Auto-close when scrolling
    window.addEventListener('scroll', () => {
        customSelect.classList.remove('open');
        optionsContainer.classList.remove('open');
    }, { passive: true });
    
    // Also bind to sidebar scrolling if it's in a sidebar
    const sidebar = wrapper.closest('.lightbox-sidebar') || wrapper.closest('.sidebar');
    if (sidebar) {
        sidebar.addEventListener('scroll', () => {
            customSelect.classList.remove('open');
            optionsContainer.classList.remove('open');
        }, { passive: true });
    }
}

document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select.open').forEach(el => el.classList.remove('open'));
    document.querySelectorAll('.custom-select-options.open').forEach(el => el.classList.remove('open'));
});

const selectObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
                if (node.tagName === 'SELECT') {
                    modernizeSelect(node);
                } else {
                    node.querySelectorAll('select').forEach(modernizeSelect);
                }
            }
        });
    });
});

selectObserver.observe(document.body, { childList: true, subtree: true });

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('select').forEach(modernizeSelect);
});
