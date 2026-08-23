// Select Modernizer script
function modernizeSelect(selectElement) {
    if (selectElement.dataset.modernized === 'true') {
        // Already modernized, maybe update it?
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
    
    customSelect.appendChild(trigger);
    customSelect.appendChild(optionsContainer);
    wrapper.appendChild(customSelect);
    
    selectElement.parentNode.insertBefore(wrapper, selectElement.nextSibling);

    const rebuildOptions = () => {
        optionsContainer.innerHTML = '';
        textSpan.textContent = selectElement.options[selectElement.selectedIndex]?.text || '';
        
        Array.from(selectElement.options).forEach((opt, index) => {
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
                selectElement.dispatchEvent(new Event('change', { bubbles: true }));
            });
            
            optionsContainer.appendChild(optionDiv);
        });
    };
    
    rebuildOptions();
    
    // Watch for dynamic option changes in the original select
    const optionObserver = new MutationObserver(rebuildOptions);
    optionObserver.observe(selectElement, { childList: true, subtree: true, characterData: true });
    
    // Sync if original select value changes programmatically
    selectElement.addEventListener('change', () => {
        textSpan.textContent = selectElement.options[selectElement.selectedIndex]?.text || '';
        optionsContainer.querySelectorAll('.custom-option').forEach((el, i) => {
            el.classList.toggle('selected', i === selectElement.selectedIndex);
        });
    });
    
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        document.querySelectorAll('.custom-select.open').forEach(el => {
            if (el !== customSelect) el.classList.remove('open');
        });
        customSelect.classList.toggle('open');
    });
}

document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select.open').forEach(el => el.classList.remove('open'));
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
