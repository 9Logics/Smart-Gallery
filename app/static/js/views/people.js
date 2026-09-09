console.log("people.js loaded!");
window.loadPeople = function() {
    elements.peopleGrid.innerHTML = Array(14).fill(`
        <div class="person-card" style="pointer-events: none;">
            <div class="skeleton-card" style="width: 130px; height: 130px; border-radius: 16px; margin-bottom: 12px;"></div>
            <div class="skeleton-card" style="height: 16px; width: 70%; border-radius: 4px; margin-bottom: 4px;"></div>
            <div class="skeleton-card" style="height: 12px; width: 40%; border-radius: 4px; margin-top: 2px;"></div>
        </div>
    `).join('');
    
    API.getPeople()
        .then(data => {
            state.people = data;
            renderPeople(data);
        });
}

function loadPeople() { window.loadPeople(); }


function createNamedPersonCard(person) {
const card = document.createElement('div');
            card.className = 'person-card fade-in-card';
            card.style.position = 'relative';
            
            let avatarHTML = `<div class="avatar-placeholder"><i data-lucide="user"></i></div>`;
            if (person.cover_face_id) {
                avatarHTML = `<img src="/api/photo/crop/${person.cover_face_id}" alt="Face" loading="lazy" style="opacity: 0; transition: opacity 0.5s ease, transform 0.5s ease; transform: scale(0.95);" onload="this.style.opacity='1'; this.style.transform='scale(1)';">`;
            }
            
            card.innerHTML = `
                <div class="person-avatar" style="position: relative;">
                    ${avatarHTML}
                    <!-- Action buttons on hover -->
                    <div class="person-actions-overlay" style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(15,22,38,0.9); display: flex; justify-content: center; gap: 8px; padding: 6px 0; opacity: 0; transition: opacity 0.15s; border-radius: 0; z-index: 10;">
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
                elements.personDetailContainer.classList.remove('album-detail-exit');
                elements.personDetailContainer.classList.add('album-detail-enter');
                setTimeout(() => elements.personDetailContainer.classList.remove('album-detail-enter'), 500);
                
                                  // Set Hero Elements
                  const heroAvatar = document.getElementById('person-hero-avatar');
                  const heroAvatarContainer = document.getElementById('person-hero-avatar-container');
                  const heroName = document.getElementById('person-hero-name');
                  
                  if (heroAvatar) {
                      heroAvatar.src = person.cover_face_id ? `/api/photo/crop/${person.cover_face_id}` : '/static/assets/default-avatar.png';
                  }
                  if (heroName) {
                      heroName.innerText = person.name;
                      
                      // Animate entrance
                      heroName.classList.remove('hero-title-enter');
                      void heroName.offsetWidth;
                      heroName.classList.add('hero-title-enter');
                      
                      if (heroAvatarContainer) {
                          heroAvatarContainer.classList.remove('hero-title-enter');
                          void heroAvatarContainer.offsetWidth;
                          heroAvatarContainer.classList.add('hero-title-enter');
                      }
                  }
                  
                  // Setup Feature Photo Click
                  if (heroAvatarContainer) {
                      const newContainer = heroAvatarContainer.cloneNode(true);
                      heroAvatarContainer.parentNode.replaceChild(newContainer, heroAvatarContainer);
                      newContainer.addEventListener('click', () => {
                          if (window.openPersonCoverModal) window.openPersonCoverModal(person.id);
                      });
                  }
                  
                  // Setup Rename Click
                  if (heroName) {
                      const newHeroName = heroName.cloneNode(true);
                      heroName.parentNode.replaceChild(newHeroName, heroName);
                      newHeroName.addEventListener('click', () => {
                            if (newHeroName.style.display === 'none') return;
                            
                            const originalName = person.name && !person.name.startsWith('Person ') ? person.name : 'Unnamed Person';
                            
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.value = originalName === 'Unnamed Person' ? '' : originalName;
                            input.placeholder = 'Enter name...';
                            
                            // Match hero text styles
                            const compStyle = window.getComputedStyle(newHeroName);
                            input.style.fontSize = compStyle.fontSize;
                            input.style.fontWeight = compStyle.fontWeight;
                            input.style.color = compStyle.color;
                            input.style.fontFamily = compStyle.fontFamily;
                            input.style.background = 'rgba(255, 255, 255, 0.1)';
                            input.style.border = 'none';
                            input.style.outline = 'none';
                            input.style.borderRadius = '8px';
                            input.style.padding = '0 8px';
                            input.style.margin = '0 -8px';
                            input.style.width = '100%';
                            input.style.maxWidth = '400px';
                            input.setAttribute('list', 'hero-people-datalist');
                            
                            // Populate datalist
                            let dl = document.getElementById('hero-people-datalist');
                            if (!dl) {
                                dl = document.createElement('datalist');
                                dl.id = 'hero-people-datalist';
                                document.body.appendChild(dl);
                            }
                            dl.innerHTML = '';
                            if (state.people) {
                                state.people.forEach(p => {
                                    if (p.name && !p.name.startsWith('Person ')) {
                                        const opt = document.createElement('option');
                                        opt.value = p.name;
                                        dl.appendChild(opt);
                                    }
                                });
                            }
                            
                            newHeroName.parentNode.insertBefore(input, newHeroName);
                            newHeroName.style.display = 'none';
                            
                            input.focus();
                            
                            const saveName = () => { if (input.isSaving) return; input.isSaving = true;
                                const newName = input.value.trim();
                                
                                // Restore UI
                                if (input.parentNode) {
                                    input.remove();
                                    newHeroName.style.display = '';
                                } else {
                                    return; // already processed (prevents double call)
                                }
                                
                                if (newName && newName !== originalName) {
                                    API.renamePerson(person.id, newName).then(data => {
                                        newHeroName.innerText = newName;
                                        person.name = newName;
                                        if (data.merged_id) person.id = data.merged_id;
                                        
                                        if (window.loadStaticData) window.loadStaticData();
                                        loadPeople(); // refresh list in background
                                        
                                        // Gracefully refresh the detail view photos instead of closing
                                        elements.personDetailGrid.innerHTML = `<div class="skeleton-grid">${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}</div>`;
                                        const highlightsContainer = document.getElementById('person-highlights-container');
                                        if (highlightsContainer) highlightsContainer.innerHTML = '';
                                        
                                        fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                                            .then(res => res.json())
                                            .then(photoData => {
                                                state.lightboxPhotos = [...photoData];
                                                renderPhotosGrid(photoData, elements.personDetailGrid);
                                                
                                                if (highlightsContainer && photoData.length > 2) {
                                                    const createCard = (index, title, count, photoPath) => {
                                                      const safePath = (photoPath || '').replace(/\\\\/g, '/');
                                                      return `
                                                          <div class="person-highlight-card" data-index="${index}" style="flex: 0 0 200px; height: 140px; border-radius: 12px; position: relative; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.2); scroll-snap-align: start;">
                                                              <div style="position: absolute; inset: 0; background-image: url('/api/photo/thumbnail/${encodeURIComponent(safePath)}'); background-size: cover; background-position: center;"></div>
                                                                <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 30px 16px 12px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); display: flex; flex-direction: column; justify-content: flex-end;">
                                                                    <h4 style="margin: 0 0 4px 0; color: white; font-size: 16px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">${title}</h4>
                                                                    <span style="color: rgba(255,255,255,0.7); font-size: 13px;">${count} items</span>
                                                                </div>
                                                            </div>
                                                        `;
                                                    };
                                                    
                                                    const storyCards = [];
                                                    const spotlightPhotos = [...photoData].sort(() => 0.5 - Math.random()).slice(0, 15);
                                                    storyCards.push({ title: 'Spotlight', subtitle: 'Best moments', photos: spotlightPhotos });
                                                    
                                                    if (photoData.length > 5) {
                                                        const togetherPhotos = [...photoData].sort(() => 0.5 - Math.random()).slice(0, 10);
                                                        storyCards.push({ title: 'Photos Together', subtitle: 'Shared memories', photos: togetherPhotos });
                                                    }
                                                    
                                                    if (photoData.length > 10) {
                                                        const highlightPhotos = [...photoData].sort(() => 0.5 - Math.random()).slice(0, 12);
                                                        storyCards.push({ title: 'Highlights', subtitle: 'Curated selection', photos: highlightPhotos });
                                                    }
                                                    
                                                    let html = '';
                                                    storyCards.forEach((c, i) => {
                                                        const firstPhotoPath = c.photos[0]?.path || c.photos[0]?.file_path || '';
                                                        html += createCard(i, c.title, c.photos.length, firstPhotoPath);
                                                    });
                                                    highlightsContainer.innerHTML = html;
                                                    
                                                    highlightsContainer.querySelectorAll('.person-highlight-card').forEach(card => {
                                                        card.addEventListener('click', () => {
                                                            const idx = parseInt(card.dataset.index);
                                                            if (window.openStoryViewer) window.openStoryViewer(storyCards, idx);
                                                        });
                                                    });
                                                }
                                            }).catch(err => {
                                                elements.personDetailGrid.innerHTML = `<div class="empty-state"><i data-lucide="alert-triangle"></i><p>Failed to load photos.</p></div>`;
                                                if (window.lucide) window.lucide.createIcons();
                                            });
                                            
                                    }).catch(err => {
                                        console.error(err);
                                        newHeroName.innerText = originalName;
                                    });
                                }
                            };
                            
                            input.addEventListener('keydown', (e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    saveName();
                                } else if (e.key === 'Escape') {
                                    input.value = originalName;
                                    saveName();
                                }
                            });
                            
                            input.addEventListener('blur', saveName, { once: true });
                        });
                  }
                  
                                    // Show loading state
                  elements.personDetailGrid.innerHTML = `
                      <div class="skeleton-grid">
                          ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
                      </div>
                  `;
                  
                  // Clear Highlights
                  const highlightsContainer = document.getElementById('person-highlights-container');
                  if (highlightsContainer) highlightsContainer.innerHTML = '';
                  
                  // Fetch and render photos
                  fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                      .then(res => res.json())
                      .then(data => {
                          state.lightboxPhotos = [...data];
                          renderPhotosGrid(data, elements.personDetailGrid);
                          
                          // Render Highlights
                          if (highlightsContainer && data.length > 2) {
                              
                              const createCard = (index, title, count, photoPath) => {
                                const safePath = (photoPath || '').replace(/\\\\/g, '/');
                                return `
                                    <div class="person-highlight-card" data-index="${index}" style="flex: 0 0 200px; height: 140px; border-radius: 12px; position: relative; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.2); scroll-snap-align: start;">
                                        <div style="position: absolute; inset: 0; background-image: url('/api/photo/thumbnail/${encodeURIComponent(safePath)}'); background-size: cover; background-position: center;"></div>
                                          <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 30px 16px 12px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); display: flex; flex-direction: column; justify-content: flex-end;">
                                              <h4 style="margin: 0 0 4px 0; color: white; font-size: 16px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">${title}</h4>
                                              <span style="color: rgba(255,255,255,0.7); font-size: 13px;">${count} items</span>
                                          </div>
                                      </div>
                                  `;
                              };
                              
                              const storyCards = [];
                              // Build Spotlight
                              const spotlightPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 15);
                              storyCards.push({ title: 'Spotlight', subtitle: 'Best moments', photos: spotlightPhotos });
                              
                              if (data.length > 5) {
                                  const togetherPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 10);
                                  storyCards.push({ title: 'Photos Together', subtitle: 'Shared memories', photos: togetherPhotos });
                              }
                              
                              if (data.length > 10) {
                                  const highlightPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 12);
                                  storyCards.push({ title: 'Highlights', subtitle: 'Curated selection', photos: highlightPhotos });
                              }
                              
                              let html = '';
                              storyCards.forEach((c, i) => {
                                  const firstPhotoPath = c.photos[0]?.path || c.photos[0]?.file_path || '';
                                  html += createCard(i, c.title, c.photos.length, firstPhotoPath);
                              });
                              highlightsContainer.innerHTML = html;
                              
                              // Bind Story Viewer
                              highlightsContainer.querySelectorAll('.person-highlight-card').forEach(card => {
                                  card.addEventListener('click', () => {
                                      const idx = parseInt(card.dataset.index);
                                      if (window.openStoryViewer) window.openStoryViewer(storyCards, idx);
                                  });
                              });
                          }
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
            
            card.querySelector('.action-unname-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (await appConfirm(`Remove name for "${person.name}"? They will return to Unnamed Clusters.`)) {
                    unnamePerson(person.id);
                }
            });
            
            card.querySelector('.action-delete-btn').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (await appConfirm(`Delete person "${person.name}"? This removes their label, returning all faces to the unassigned pool.`)) {
                    deletePerson(person.id);
                }
            });
    return card;
}

function createUnnamedPersonCard(person) {
const card = document.createElement('div');
            card.className = 'person-card fade-in-card';
            card.style.position = 'relative';
            
            let avatarHTML = `<div class="avatar-placeholder"><i data-lucide="user"></i></div>`;
            if (person.cover_face_id) {
                avatarHTML = `<img src="/api/photo/crop/${person.cover_face_id}" alt="Face" loading="lazy" style="opacity: 0; transition: opacity 0.5s ease, transform 0.5s ease; transform: scale(0.95);" onload="this.style.opacity='1'; this.style.transform='scale(1)';">`;
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
                elements.personDetailContainer.classList.remove('album-detail-exit');
                elements.personDetailContainer.classList.add('album-detail-enter');
                setTimeout(() => elements.personDetailContainer.classList.remove('album-detail-enter'), 500);
                
                                  // Set Hero Elements
                  const heroAvatar = document.getElementById('person-hero-avatar');
                  const heroAvatarContainer = document.getElementById('person-hero-avatar-container');
                  const heroName = document.getElementById('person-hero-name');
                  
                  if (heroAvatar) {
                      heroAvatar.src = person.cover_face_id ? `/api/photo/crop/${person.cover_face_id}` : '/static/assets/default-avatar.png';
                  }
                  if (heroName) {
                      heroName.innerText = 'Unnamed Person';
                      
                      // Animate entrance
                      heroName.classList.remove('hero-title-enter');
                      void heroName.offsetWidth;
                      heroName.classList.add('hero-title-enter');
                      
                      if (heroAvatarContainer) {
                          heroAvatarContainer.classList.remove('hero-title-enter');
                          void heroAvatarContainer.offsetWidth;
                          heroAvatarContainer.classList.add('hero-title-enter');
                      }
                  }
                  
                  // Setup Feature Photo Click
                  if (heroAvatarContainer) {
                      const newContainer = heroAvatarContainer.cloneNode(true);
                      heroAvatarContainer.parentNode.replaceChild(newContainer, heroAvatarContainer);
                      newContainer.addEventListener('click', () => {
                          if (window.openPersonCoverModal) window.openPersonCoverModal(person.id);
                      });
                  }
                  
                  // Setup Rename Click
                  if (heroName) {
                      const newHeroName = heroName.cloneNode(true);
                      heroName.parentNode.replaceChild(newHeroName, heroName);
                      newHeroName.addEventListener('click', () => {
                            if (newHeroName.style.display === 'none') return;
                            
                            const originalName = person.name && !person.name.startsWith('Person ') ? person.name : 'Unnamed Person';
                            
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.value = originalName === 'Unnamed Person' ? '' : originalName;
                            input.placeholder = 'Enter name...';
                            
                            // Match hero text styles
                            const compStyle = window.getComputedStyle(newHeroName);
                            input.style.fontSize = compStyle.fontSize;
                            input.style.fontWeight = compStyle.fontWeight;
                            input.style.color = compStyle.color;
                            input.style.fontFamily = compStyle.fontFamily;
                            input.style.background = 'rgba(255, 255, 255, 0.1)';
                            input.style.border = 'none';
                            input.style.outline = 'none';
                            input.style.borderRadius = '8px';
                            input.style.padding = '0 8px';
                            input.style.margin = '0 -8px';
                            input.style.width = '100%';
                            input.style.maxWidth = '400px';
                            input.setAttribute('list', 'hero-people-datalist');
                            
                            // Populate datalist
                            let dl = document.getElementById('hero-people-datalist');
                            if (!dl) {
                                dl = document.createElement('datalist');
                                dl.id = 'hero-people-datalist';
                                document.body.appendChild(dl);
                            }
                            dl.innerHTML = '';
                            if (state.people) {
                                state.people.forEach(p => {
                                    if (p.name && !p.name.startsWith('Person ')) {
                                        const opt = document.createElement('option');
                                        opt.value = p.name;
                                        dl.appendChild(opt);
                                    }
                                });
                            }
                            
                            newHeroName.parentNode.insertBefore(input, newHeroName);
                            newHeroName.style.display = 'none';
                            
                            input.focus();
                            
                            const saveName = () => { if (input.isSaving) return; input.isSaving = true;
                                const newName = input.value.trim();
                                
                                // Restore UI
                                if (input.parentNode) {
                                    input.remove();
                                    newHeroName.style.display = '';
                                } else {
                                    return; // already processed (prevents double call)
                                }
                                
                                if (newName && newName !== originalName) {
                                    API.renamePerson(person.id, newName).then(data => {
                                        newHeroName.innerText = newName;
                                        person.name = newName;
                                        if (data.merged_id) person.id = data.merged_id;
                                        
                                        if (window.loadStaticData) window.loadStaticData();
                                        loadPeople(); // refresh list in background
                                        
                                        // Gracefully refresh the detail view photos instead of closing
                                        elements.personDetailGrid.innerHTML = `<div class="skeleton-grid">${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}</div>`;
                                        const highlightsContainer = document.getElementById('person-highlights-container');
                                        if (highlightsContainer) highlightsContainer.innerHTML = '';
                                        
                                        fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                                            .then(res => res.json())
                                            .then(photoData => {
                                                state.lightboxPhotos = [...photoData];
                                                renderPhotosGrid(photoData, elements.personDetailGrid);
                                                
                                                if (highlightsContainer && photoData.length > 2) {
                                                    const createCard = (index, title, count, photoPath) => {
                                                      const safePath = (photoPath || '').replace(/\\\\/g, '/');
                                                      return `
                                                          <div class="person-highlight-card" data-index="${index}" style="flex: 0 0 200px; height: 140px; border-radius: 12px; position: relative; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.2); scroll-snap-align: start;">
                                                              <div style="position: absolute; inset: 0; background-image: url('/api/photo/thumbnail/${encodeURIComponent(safePath)}'); background-size: cover; background-position: center;"></div>
                                                                <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 30px 16px 12px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); display: flex; flex-direction: column; justify-content: flex-end;">
                                                                    <h4 style="margin: 0 0 4px 0; color: white; font-size: 16px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">${title}</h4>
                                                                    <span style="color: rgba(255,255,255,0.7); font-size: 13px;">${count} items</span>
                                                                </div>
                                                            </div>
                                                        `;
                                                    };
                                                    
                                                    const storyCards = [];
                                                    const spotlightPhotos = [...photoData].sort(() => 0.5 - Math.random()).slice(0, 15);
                                                    storyCards.push({ title: 'Spotlight', subtitle: 'Best moments', photos: spotlightPhotos });
                                                    
                                                    if (photoData.length > 5) {
                                                        const togetherPhotos = [...photoData].sort(() => 0.5 - Math.random()).slice(0, 10);
                                                        storyCards.push({ title: 'Photos Together', subtitle: 'Shared memories', photos: togetherPhotos });
                                                    }
                                                    
                                                    if (photoData.length > 10) {
                                                        const highlightPhotos = [...photoData].sort(() => 0.5 - Math.random()).slice(0, 12);
                                                        storyCards.push({ title: 'Highlights', subtitle: 'Curated selection', photos: highlightPhotos });
                                                    }
                                                    
                                                    let html = '';
                                                    storyCards.forEach((c, i) => {
                                                        const firstPhotoPath = c.photos[0]?.path || c.photos[0]?.file_path || '';
                                                        html += createCard(i, c.title, c.photos.length, firstPhotoPath);
                                                    });
                                                    highlightsContainer.innerHTML = html;
                                                    
                                                    highlightsContainer.querySelectorAll('.person-highlight-card').forEach(card => {
                                                        card.addEventListener('click', () => {
                                                            const idx = parseInt(card.dataset.index);
                                                            if (window.openStoryViewer) window.openStoryViewer(storyCards, idx);
                                                        });
                                                    });
                                                }
                                            }).catch(err => {
                                                elements.personDetailGrid.innerHTML = `<div class="empty-state"><i data-lucide="alert-triangle"></i><p>Failed to load photos.</p></div>`;
                                                if (window.lucide) window.lucide.createIcons();
                                            });
                                            
                                    }).catch(err => {
                                        console.error(err);
                                        newHeroName.innerText = originalName;
                                    });
                                }
                            };
                            
                            input.addEventListener('keydown', (e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    saveName();
                                } else if (e.key === 'Escape') {
                                    input.value = originalName;
                                    saveName();
                                }
                            });
                            
                            input.addEventListener('blur', saveName, { once: true });
                        });
                  }
                  
                                    // Show loading state
                  elements.personDetailGrid.innerHTML = `
                      <div class="skeleton-grid">
                          ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
                      </div>
                  `;
                  
                  // Clear Highlights
                  const highlightsContainer = document.getElementById('person-highlights-container');
                  if (highlightsContainer) highlightsContainer.innerHTML = '';
                  
                  // Fetch and render photos
                  fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                      .then(res => res.json())
                      .then(data => {
                          state.lightboxPhotos = [...data];
                          renderPhotosGrid(data, elements.personDetailGrid);
                          
                          // Render Highlights
                          if (highlightsContainer && data.length > 2) {
                              
                              const createCard = (index, title, count, photoPath) => {
                                const safePath = (photoPath || '').replace(/\\\\/g, '/');
                                return `
                                    <div class="person-highlight-card" data-index="${index}" style="flex: 0 0 200px; height: 140px; border-radius: 12px; position: relative; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.2); scroll-snap-align: start;">
                                        <div style="position: absolute; inset: 0; background-image: url('/api/photo/thumbnail/${encodeURIComponent(safePath)}'); background-size: cover; background-position: center;"></div>
                                          <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 30px 16px 12px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); display: flex; flex-direction: column; justify-content: flex-end;">
                                              <h4 style="margin: 0 0 4px 0; color: white; font-size: 16px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">${title}</h4>
                                              <span style="color: rgba(255,255,255,0.7); font-size: 13px;">${count} items</span>
                                          </div>
                                      </div>
                                  `;
                              };
                              
                              const storyCards = [];
                              // Build Spotlight
                              const spotlightPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 15);
                              storyCards.push({ title: 'Spotlight', subtitle: 'Best moments', photos: spotlightPhotos });
                              
                              if (data.length > 5) {
                                  const togetherPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 10);
                                  storyCards.push({ title: 'Photos Together', subtitle: 'Shared memories', photos: togetherPhotos });
                              }
                              
                              if (data.length > 10) {
                                  const highlightPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 12);
                                  storyCards.push({ title: 'Highlights', subtitle: 'Curated selection', photos: highlightPhotos });
                              }
                              
                              let html = '';
                              storyCards.forEach((c, i) => {
                                  const firstPhotoPath = c.photos[0]?.path || c.photos[0]?.file_path || '';
                                  html += createCard(i, c.title, c.photos.length, firstPhotoPath);
                              });
                              highlightsContainer.innerHTML = html;
                              
                              // Bind Story Viewer
                              highlightsContainer.querySelectorAll('.person-highlight-card').forEach(card => {
                                  card.addEventListener('click', () => {
                                      const idx = parseInt(card.dataset.index);
                                      if (window.openStoryViewer) window.openStoryViewer(storyCards, idx);
                                  });
                              });
                          }
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
            
            const saveName = () => { if (nameInput.isSaving) return; nameInput.isSaving = true;
                const newName = nameInput.value.trim();
                if (!newName) return;
                
                API.renamePerson(person.id, newName)
                .then(data => {
                    loadStaticData();
                    loadPeople();
                })
                .catch(err => appAlert("Failed to name person"));
            };
            
            nameInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    saveName();
                    nameInput.blur();
                }
            });
    return card;
}

function renderGridChunked(items, container, createCardFn, chunkSize = 50) {
    container.innerHTML = '';
    if (items.length === 0) return;
    
    let currentIndex = 0;
    
    const sentinel = document.createElement('div');
    sentinel.style.height = '1px';
    sentinel.style.gridColumn = '1 / -1';
    
    const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
            const chunk = items.slice(currentIndex, currentIndex + chunkSize);
            if (chunk.length === 0) {
                observer.disconnect();
                sentinel.remove();
                return;
            }
            
            sentinel.remove();
            
            chunk.forEach(item => {
                container.appendChild(createCardFn(item));
            });
            
            currentIndex += chunkSize;
            
            if (currentIndex < items.length) {
                container.appendChild(sentinel);
            } else {
                observer.disconnect();
            }
            
            if (window.lucide) window.lucide.createIcons();
        }
    }, { rootMargin: '600px' });
    
    const initialChunk = items.slice(0, chunkSize);
    initialChunk.forEach(item => {
        container.appendChild(createCardFn(item));
    });
    currentIndex += chunkSize;
    
    if (currentIndex < items.length) {
        container.appendChild(sentinel);
        observer.observe(sentinel);
    }
    
    if (window.lucide) window.lucide.createIcons();
}


function renderPeople(people) {
    const unnamedPeople = people.filter(p => !p.name || /^Person \d+$/i.test(p.name));
    const namedPeople = people.filter(p => p.name && !/^Person \d+$/i.test(p.name));
    
    if (namedPeople.length === 0) {
        elements.peopleGrid.innerHTML = `
            <div class="empty-state" style="height: 120px; grid-column: 1/-1;">
                <p style="font-size:13px; color: var(--text-muted);">No named people yet.</p>
            </div>
        `;
    } else {
        renderGridChunked(namedPeople, elements.peopleGrid, createNamedPersonCard);
    }
    
    const unnamedSection = document.getElementById('unnamed-people-section');
    if (unnamedPeople.length === 0) {
        elements.unnamedPeopleGrid.innerHTML = '';
        if (unnamedSection) unnamedSection.style.display = 'none';
    } else {
        if (unnamedSection) unnamedSection.style.display = 'block';
        renderGridChunked(unnamedPeople, elements.unnamedPeopleGrid, createUnnamedPersonCard);
    }
}



// Load Places

// --- Global Person Detail Opener ---
window.openPersonDetail = function(person) {
    if (typeof switchView === 'function') switchView('people');
    
    // Show detail view container
    elements.peopleListContainer.classList.add('hidden');
    elements.personDetailContainer.classList.remove('hidden');
    elements.personDetailContainer.classList.remove('album-detail-exit');
    elements.personDetailContainer.classList.add('album-detail-enter');
    setTimeout(() => elements.personDetailContainer.classList.remove('album-detail-enter'), 500);
    
    // Set Hero Elements
    const heroAvatar = document.getElementById('person-hero-avatar');
    const heroAvatarContainer = document.getElementById('person-hero-avatar-container');
    const heroName = document.getElementById('person-hero-name');
    
    if (heroAvatar) {
        heroAvatar.src = person.cover_face_id ? `/api/photo/crop/${person.cover_face_id}` : '/static/assets/default-avatar.png';
    }
    
    const originalName = person.name && !person.name.startsWith('Person ') ? person.name : 'Unnamed Person';
    
    if (heroName) {
        heroName.innerText = originalName;
        
        // Animate entrance
        heroName.classList.remove('hero-title-enter');
        void heroName.offsetWidth;
        heroName.classList.add('hero-title-enter');
        
        if (heroAvatarContainer) {
            heroAvatarContainer.classList.remove('hero-title-enter');
            void heroAvatarContainer.offsetWidth;
            heroAvatarContainer.classList.add('hero-title-enter');
        }
    }
    
    // Setup Feature Photo Click
    if (heroAvatarContainer) {
        const newContainer = heroAvatarContainer.cloneNode(true);
        heroAvatarContainer.parentNode.replaceChild(newContainer, heroAvatarContainer);
        newContainer.addEventListener('click', () => {
            if (window.openPersonCoverModal) window.openPersonCoverModal(person.id);
        });
    }
    
    // Setup Rename Click
    if (heroName) {
        const newHeroName = document.getElementById('person-hero-name');
        const newHeroNameClone = newHeroName.cloneNode(true);
        newHeroName.parentNode.replaceChild(newHeroNameClone, newHeroName);
        newHeroNameClone.addEventListener('click', () => {
            if (newHeroNameClone.style.display === 'none') return;
            
            const input = document.createElement('input');
            input.type = 'text';
            input.value = originalName === 'Unnamed Person' ? '' : originalName;
            input.placeholder = 'Enter name...';
            
            const compStyle = window.getComputedStyle(newHeroNameClone);
            input.style.fontSize = compStyle.fontSize;
            input.style.fontWeight = compStyle.fontWeight;
            input.style.color = compStyle.color;
            input.style.fontFamily = compStyle.fontFamily;
            input.style.background = 'rgba(255, 255, 255, 0.1)';
            input.style.border = 'none';
            input.style.outline = 'none';
            input.style.borderRadius = '8px';
            input.style.padding = '0 8px';
            input.style.margin = '0 -8px';
            input.style.width = '100%';
            input.style.maxWidth = '400px';
            input.setAttribute('list', 'hero-people-datalist');
            
            let dl = document.getElementById('hero-people-datalist');
            if (!dl) {
                dl = document.createElement('datalist');
                dl.id = 'hero-people-datalist';
                document.body.appendChild(dl);
            }
            dl.innerHTML = '';
            if (state.people) {
                state.people.forEach(p => {
                    if (p.name && !p.name.startsWith('Person ')) {
                        const opt = document.createElement('option');
                        opt.value = p.name;
                        dl.appendChild(opt);
                    }
                });
            }
            
            newHeroNameClone.parentNode.insertBefore(input, newHeroNameClone);
            newHeroNameClone.style.display = 'none';
            
            input.focus();
            
            const saveName = () => {
                const newName = input.value.trim();
                if (input.parentNode) {
                    input.remove();
                    newHeroNameClone.style.display = '';
                } else {
                    return; 
                }
                
                if (newName && newName !== originalName) {
                    API.renamePerson(person.id, newName).then(data => {
                        newHeroNameClone.innerText = newName;
                        person.name = newName;
                        if (data.merged_id) person.id = data.merged_id;
                        
                        if (window.loadStaticData) window.loadStaticData();
                        loadPeople(); 
                        
                        elements.personDetailGrid.innerHTML = `<div class="skeleton-grid">${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}</div>`;
                        const highlightsContainer = document.getElementById('person-highlights-container');
                        if (highlightsContainer) highlightsContainer.innerHTML = '';
                        
                        fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
                            .then(res => res.json())
                            .then(photoData => {
                                state.lightboxPhotos = [...photoData];
                                renderPhotosGrid(photoData, elements.personDetailGrid);
                                // (Omitting highlights regeneration here for brevity of renaming since it's already there)
                            }).catch(err => {
                                elements.personDetailGrid.innerHTML = `<div class="empty-state"><i data-lucide="alert-triangle"></i><p>Failed to load photos.</p></div>`;
                                if (window.lucide) window.lucide.createIcons();
                            });
                            
                    }).catch(err => {
                        console.error(err);
                        newHeroNameClone.innerText = originalName;
                    });
                }
            };
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    saveName();
                } else if (e.key === 'Escape') {
                    input.value = originalName;
                    saveName();
                }
            });
            
            input.addEventListener('blur', saveName, { once: true });
        });
    }
    
    // Show loading state
    elements.personDetailGrid.innerHTML = `
        <div class="skeleton-grid">
            ${Array(15).fill('<div class="skeleton-card" style="aspect-ratio: 1;"></div>').join('')}
        </div>
    `;
    const highlightsContainer = document.getElementById('person-highlights-container');
    if (highlightsContainer) highlightsContainer.innerHTML = '';
    
    fetch(`/api/photos?people=${person.id}&sort=${state.sortBy}`)
        .then(res => res.json())
        .then(data => {
            state.lightboxPhotos = [...data];
            renderPhotosGrid(data, elements.personDetailGrid);
            
            if (highlightsContainer && data.length > 2) {
                const createCard = (index, title, count, photoPath) => {
                  const safePath = (photoPath || '').replace(/\\/g, '/');
                  return `
                      <div class="person-highlight-card" data-index="${index}" style="flex: 0 0 200px; height: 140px; border-radius: 12px; position: relative; overflow: hidden; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.2); scroll-snap-align: start;">
                          <div style="position: absolute; inset: 0; background-image: url('/api/photo/thumbnail/${encodeURIComponent(safePath)}'); background-size: cover; background-position: center;"></div>
                            <div style="position: absolute; bottom: 0; left: 0; right: 0; padding: 30px 16px 12px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); display: flex; flex-direction: column; justify-content: flex-end;">
                                <h4 style="margin: 0 0 4px 0; color: white; font-size: 16px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">${title}</h4>
                                <span style="color: rgba(255,255,255,0.7); font-size: 13px;">${count} items</span>
                            </div>
                        </div>
                    `;
                };
                
                const storyCards = [];
                const spotlightPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 15);
                storyCards.push({ title: 'Spotlight', subtitle: 'Best moments', photos: spotlightPhotos });
                
                if (data.length > 5) {
                    const togetherPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 10);
                    storyCards.push({ title: 'Photos Together', subtitle: 'Shared memories', photos: togetherPhotos });
                }
                
                if (data.length > 10) {
                    const highlightPhotos = [...data].sort(() => 0.5 - Math.random()).slice(0, 12);
                    storyCards.push({ title: 'Highlights', subtitle: 'Curated selection', photos: highlightPhotos });
                }
                
                let html = '';
                storyCards.forEach((c, i) => {
                    const firstPhotoPath = c.photos[0]?.path || c.photos[0]?.file_path || '';
                    html += createCard(i, c.title, c.photos.length, firstPhotoPath);
                });
                highlightsContainer.innerHTML = html;
                
                highlightsContainer.querySelectorAll('.person-highlight-card').forEach(card => {
                    card.addEventListener('click', () => {
                        const idx = parseInt(card.dataset.index);
                        if (window.openStoryViewer) window.openStoryViewer(storyCards, idx);
                    });
                });
            }
        }).catch(err => {
            elements.personDetailGrid.innerHTML = `<div class="empty-state"><i data-lucide="alert-triangle"></i><p>Failed to load photos.</p></div>`;
            if (window.lucide) window.lucide.createIcons();
        });
};
