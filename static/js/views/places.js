function loadPlaces() {
    elements.placesGrid.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading place data...</p>
        </div>
    `;
    
    // Load both grid data and map data
    Promise.all([
        fetch('/api/places').then(r => r.json()),
        fetch('/api/places/map_data').then(r => r.json())
    ]).then(([gridData, mapData]) => {
        state.places = gridData;
        state.placesMapData = mapData;
        
        renderPlaces(gridData);
        renderPlacesMap(mapData);
    });
}

function renderPlacesMap(mapData) {
    const mapContainer = document.getElementById('places-main-map');
    if (!mapContainer) return;
    
    // Initialize map if not already done
    if (!state.placesMapInstance) {
        state.placesMapInstance = L.map('places-main-map');
        
        // Add custom class for CSS inversion (Dark Mode + Transit)
        const mapEl = document.getElementById('places-main-map');
        mapEl.classList.add('dark-transit-map');
        
        // OpenStreetMap default has excellent street & public transport highlighting
        // When combined with our CSS filter, it creates a perfect dark transport map
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap',
            maxZoom: 19
        }).addTo(state.placesMapInstance);
    }
    
    // Clear old layers
    state.placesMapInstance.eachLayer(layer => {
        if (layer instanceof L.MarkerClusterGroup || layer instanceof L.Marker) {
            state.placesMapInstance.removeLayer(layer);
        }
    });
    
    if (mapData.length === 0) {
        if (!state.mapViewRetained) {
            state.placesMapInstance.setView([20, 0], 2);
            state.mapViewRetained = true;
        }
        return;
    }
    
    // Create marker cluster group
    const markers = L.markerClusterGroup({
        maxClusterRadius: 60,
        iconCreateFunction: function(cluster) {
            const childCount = cluster.getChildCount();
            const children = cluster.getAllChildMarkers();
            
            // Get the first child's thumbnail for the preview
            const firstMarkerData = children[0].options.photoData;
            const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(firstMarkerData.path)}`;
            
            // Find most frequent place_name among children
            const placeCounts = {};
            let bestPlace = '';
            let maxCount = 0;
            children.forEach(c => {
                const p = c.options.photoData.place_name;
                if (p) {
                    placeCounts[p] = (placeCounts[p] || 0) + 1;
                    if (placeCounts[p] > maxCount) {
                        maxCount = placeCounts[p];
                        bestPlace = p;
                    }
                }
            });
            
            return L.divIcon({
                html: `
                    <div class="custom-cluster-blob" style="background-image: url('${thumbUrl}');" title="${bestPlace}">
                        <div class="custom-cluster-badge">
                            ${childCount}
                        </div>
                    </div>
                `,
                className: 'custom-cluster-icon',
                iconSize: L.point(56, 56)
            });
        }
    });
    
    const bounds = [];
    
    mapData.forEach(photo => {
        const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(photo.path)}`;
        const customIcon = L.divIcon({
            html: `
                <div class="custom-single-marker" style="background-image: url('${thumbUrl}');">
                </div>
            `,
            className: 'custom-single-marker-icon',
            iconSize: L.point(44, 52),
            iconAnchor: L.point(22, 52)
        });
        
        const marker = L.marker([photo.latitude, photo.longitude], { 
            photoData: photo,
            icon: customIcon
        });
        
        // Setup tooltip for smart tag name
        if (photo.place_name) {
            marker.bindTooltip(photo.place_name, { direction: 'top', className: 'place-tooltip' });
        }
        
        bounds.push([photo.latitude, photo.longitude]);
        markers.addLayer(marker);
    });
    
    // When a cluster is clicked, override zoom and open the main grid!
    markers.on('clusterclick', function (a) {
        const childMarkers = a.layer.getAllChildMarkers();
        const paths = childMarkers.map(m => m.options.photoData.path);
        
        // Create a custom filter for these specific paths
        state.filters.places = []; // Clear other place filters
        state.filters.customPaths = paths; // We will need to implement this in applyFilters
        switchView('photos');
        applyFilters();
    });
    
    // Also override single marker click
    markers.on('click', function (a) {
        const path = a.layer.options.photoData.path;
        state.filters.places = [];
        state.filters.customPaths = [path];
        switchView('photos');
        applyFilters();
    });
    
    state.placesMapInstance.addLayer(markers);
    
    // Fit bounds but ensure map renders fully first
    setTimeout(() => {
        state.placesMapInstance.invalidateSize();
        if (bounds.length > 0 && !state.mapViewRetained) {
            state.placesMapInstance.fitBounds(bounds, { padding: [50, 50] });
            state.mapViewRetained = true;
        }
    }, 300);
}

function renderPlaces(cityGroups) {
    if (!cityGroups || cityGroups.length === 0) {
        elements.placesGrid.innerHTML = `
            <div class="empty-state">
                <i data-lucide="map"></i>
                <p>No place metadata found in scanned images.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    elements.placesGrid.innerHTML = '';
    
    // Convert old placesGrid container from a grid to a block container that holds city groups
    elements.placesGrid.style.display = 'block';
    
    // Fallback: If we got the old flat structure from browser cache, wrap it in a single "All Places" group
    if (cityGroups.length > 0 && !cityGroups[0].places) {
        cityGroups = [{ city: "All Places (Refresh required)", places: cityGroups }];
    }
    
    cityGroups.forEach(group => {
        // Create City Header
        const cityHeader = document.createElement('h2');
        cityHeader.innerText = group.city;
        cityHeader.style.fontFamily = 'var(--font-display)';
        cityHeader.style.fontSize = '24px';
        cityHeader.style.marginTop = '24px';
        cityHeader.style.marginBottom = '16px';
        elements.placesGrid.appendChild(cityHeader);
        
        // Create subgrid for this city's places
        const subGrid = document.createElement('div');
        subGrid.style.display = 'grid';
        subGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(180px, 1fr))';
        subGrid.style.gap = '16px';
        subGrid.style.marginBottom = '32px';
        
        group.places.forEach(place => {
            const card = document.createElement('div');
            card.className = 'place-card';
            
            if (place.sample_path) {
                const thumbUrl = `/api/photo/thumbnail/${encodeURIComponent(place.sample_path)}`;
                card.style.cssText = `background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 60%, rgba(0,0,0,0) 100%), url('${thumbUrl}'); background-size: cover; background-position: center; border: none; color: white; display: flex; flex-direction: column; justify-content: flex-end; padding: 14px; min-height: 150px; align-items: flex-start; overflow: hidden;`;
            } else {
                card.style.cssText = `min-height: 150px;`;
            }
            
            card.innerHTML = `
                <div style="z-index: 2; position: relative; width: 100%;">
                    <h3 style="margin: 0; margin-bottom: 3px; color: white; text-shadow: 0 1px 4px rgba(0,0,0,0.8);">${place.name}</h3>
                    <span style="color: rgba(255,255,255,0.75); text-shadow: 0 1px 3px rgba(0,0,0,0.8);">${place.count} photo${place.count === 1 ? '' : 's'}</span>
                </div>
            `;
            
            card.addEventListener('click', () => {
                state.filters.customPaths = null;
                state.filters.places = [place.name];
                updateFiltersUI();
                switchView('photos');
            });
            
            subGrid.appendChild(card);
        });
        
        elements.placesGrid.appendChild(subGrid);
    });
    
    lucide.createIcons();
}

// Search Suggestions & Autocomplete Logic
