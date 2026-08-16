function loadPeople() {
    elements.peopleGrid.innerHTML = `
        <div class="skeleton-grid" style="grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));">
            ${Array(14).fill('<div class="skeleton-card" style="aspect-ratio: 1; border-radius: 50%;"></div>').join('')}
        </div>
    `;
    
    fetch('/api/people')
        .then(res => res.json())
        .then(data => {
            state.people = data;
            renderPeople(data);
        });
}

function renderPeople(people) {
    const unnamedPeople = people.filter(p => !p.name || /^Person \d+$/i.test(p.name));
    const namedPeople = people.filter(p => p.name && !/^Person \d+$/i.test(p.name));
    
    // 1. Render Named People
    elements.peopleGrid.innerHTML = '';
    if (namedPeople.length === 0) {
        elements.peopleGrid.innerHTML = `
            <div class="empty-state" style="height: 120px; grid-column: 1/-1;">
                <p style="font-size:13px; color: var(--text-muted);">No named people yet.</p>
            </div>
        `;
    } else {
        namedPeople.forEach(person => {
            const card = document.createElement('div');
            card.className = 'person-card';
            card.style.position = 'relative';
            
            let avatarHTML = `<div class="avatar-placeholder"><i data-lucide="user"></i></div>`;
            if (person.cover_face_id) {
                avatarHTML = `<img src="/api/photo/crop/${person.cover_face_id}" alt="Face">`;
            }
            
            card.innerHTML = `
                <div class="person-avatar" style="position: relative;">
                    ${avatarHTML}
                    <!-- Action buttons on hover -->
                    <div class="person-actions-overlay" style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(15,22,38,0.9); display: flex; justify-content: center; gap: 8px; padding: 6px 0; opacity: 0; transition: opacity 0.15s; border-radius: 0 0 50% 50%; z-index: 10;">
                        <button class="action-rename-btn" title="Rename" style="background:none; border:none; color:#ffffff; cursor:pointer; padding:2px; display:flex; align-items:center; justify-content:center;"><i data-lucide="edit-3" style="width:13px; height:13px;"></i></button>
                        <button class="action-unname-btn" title="Unname" style="background:none; border:none; color:#ffffff; cursor:pointer; padding:2px; display:flex; align-items:center; justify-content:center;"><i data-lucide="user-minus" style="width:13px; height:13px;"></i></button>
                        <button class="action-delete-btn" title="Remove" style="background:none; border:none; color:#ef4444; cursor:pointer; padding:2px; display:flex; align-items:center; justify-content:center;"><i data-lucide="trash-2" style="width:13px; height:13px;"></i></button>
                    </div>
                </div>
                <div class="person-name-wrapper">
                    <span class="person-name">${person.name}</span>
                </div>
                <p style="font-size:12px; color:var(--text-muted); margin-top:2px;">${person.face_count} photos</p>
            `;
            
            // Hover styles for avatar overlay
            const avatar = card.querySelector('.person-avatar');
            const overlay = card.querySelector('.person-actions-overlay');
            avatar.addEventListener('mouseenter', () => overlay.style.opacity = '1');
            avatar.addEventListener('mouseleave', () => overlay.style.opacity = '0');
            
            // Clicking card (except action overlay) filters by this person
            card.addEventListener('click', (e) => {
                if (e.target.closest('.person-actions-overlay')) return;
                
                // Show detail view container
                elements.peopleListContainer.classList.add('hidden');
                elements.personDetailContainer.classList.remove('hidden');
                
                // Set title
                elements.personDetailTitle.innerText = person.name;
                
                // Show loading state
                elements.personDetailGrid.innerHTML = `
                    <div class="skeleton-grid">
                        ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
                    </div>
                `;
                
                // Fetch and render photos
                fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                    .then(res => res.json())
                    .then(data => {
                        state.lightboxPhotos = [...data];
                        renderPhotosGrid(data, elements.personDetailGrid);
                    })
                    .catch(err => {
                        elements.personDetailGrid.innerHTML = `
                            <div class="empty-state">
                                <i data-lucide="alert-triangle"></i>
                                <p>Failed to load photos.</p>
                            </div>
                        `;
                        lucide.createIcons();
                    });
            });
            
            // Action button triggers
            card.querySelector('.action-rename-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                renamePersonPrompt(person.id, person.name);
            });
            
            card.querySelector('.action-unname-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm(`Remove name for "${person.name}"? They will return to Unnamed Clusters.`)) {
                    unnamePerson(person.id);
                }
            });
            
            card.querySelector('.action-delete-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm(`Delete person "${person.name}"? This removes their label, returning all faces to the unassigned pool.`)) {
                    deletePerson(person.id);
                }
            });
            
            elements.peopleGrid.appendChild(card);
        });
    }
    
    // 2. Render Unnamed People (bottom section)
    const unnamedSection = document.getElementById('unnamed-people-section');
    elements.unnamedPeopleGrid.innerHTML = '';
    
    if (unnamedPeople.length === 0) {
        if (unnamedSection) unnamedSection.style.display = 'none';
    } else {
        if (unnamedSection) unnamedSection.style.display = 'block';
        unnamedPeople.forEach(person => {
            const card = document.createElement('div');
            card.className = 'person-card';
            card.style.position = 'relative';
            
            let avatarHTML = `<div class="avatar-placeholder"><i data-lucide="user"></i></div>`;
            if (person.cover_face_id) {
                avatarHTML = `<img src="/api/photo/crop/${person.cover_face_id}" alt="Face">`;
            }
            
            card.innerHTML = `
                <div class="person-avatar">
                    ${avatarHTML}
                </div>
                <div class="person-name-wrapper" style="margin-top: 8px; width: 100%; display: flex; flex-direction: column; gap: 4px; align-items: center;">
                    <input type="text" class="input-text name-input-field" placeholder="Add name..." style="font-size:11px; height: 26px; padding: 0 8px; text-align: center; width: 100%; max-width: 110px; border-radius: 6px;" />
                </div>
                <p style="font-size:11px; color:var(--text-muted); margin-top:4px;">${person.face_count} photos</p>
            `;
            
            // Clicking card avatar filters photos by this person
            card.querySelector('.person-avatar').addEventListener('click', () => {
                // Show detail view container
                elements.peopleListContainer.classList.add('hidden');
                elements.personDetailContainer.classList.remove('hidden');
                
                // Set title
                elements.personDetailTitle.innerText = 'Unnamed Person';
                
                // Show loading state
                elements.personDetailGrid.innerHTML = `
                    <div class="skeleton-grid">
                        ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
                    </div>
                `;
                
                // Fetch and render photos
                fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                    .then(res => res.json())
                    .then(data => {
                        state.lightboxPhotos = [...data];
                        renderPhotosGrid(data, elements.personDetailGrid);
                    })
                    .catch(err => {
                        elements.personDetailGrid.innerHTML = `
                            <div class="empty-state">
                                <i data-lucide="alert-triangle"></i>
                                <p>Failed to load photos.</p>
                            </div>
                        `;
                        lucide.createIcons();
                    });
            });
            
            // Type name and hit Enter or lose focus to save
            const nameInput = card.querySelector('.name-input-field');
            
            const saveName = () => {
                const newName = nameInput.value.trim();
                if (!newName) return;
                
                fetch('/api/people/rename', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: person.id, name: newName })
                })
                .then(res => res.json())
                .then(data => {
                    loadStaticData();
                    loadPeople();
                })
                .catch(err => alert("Failed to name person"));
            };
            
            nameInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    saveName();
                    nameInput.blur();
                }
            });
            
            elements.unnamedPeopleGrid.appendChild(card);
        });
    }
    
    lucide.createIcons();
}


// Load Places
