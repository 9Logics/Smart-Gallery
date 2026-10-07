import codecs
import re

with codecs.open('static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add placesMap to state
state_block = """const state = {
    currentView: 'photos',
    photos: [],
    albums: [],
    places: [],
    placesMapData: [], // new
    placesMapInstance: null, // new
"""
content = content.replace("const state = {\n    currentView: 'photos',\n    photos: [],\n    albums: [],\n    places: [],", state_block)

# 2. Add Rework Grouping Button listener
rework_listener = """
document.getElementById('rework-grouping-btn')?.addEventListener('click', () => {
    const thresh = prompt("Enter Minimum Photos Threshold for Smart Grouping:", "3");
    if (thresh === null) return;
    const t = parseInt(thresh);
    if (isNaN(t) || t < 1) {
        alert("Invalid threshold.");
        return;
    }
    const btn = document.getElementById('rework-grouping-btn');
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="spin" style="width:16px;height:16px;"></i> Processing...';
    lucide.createIcons();
    
    fetch('/api/places/rework_grouping', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({threshold: t})
    }).then(res => res.json()).then(data => {
        btn.innerHTML = origHtml;
        lucide.createIcons();
        if (data.success) {
            alert("Grouping updated successfully!");
            loadPlaces(); // Reload map and grid
        } else {
            alert("Failed to update grouping.");
        }
    }).catch(err => {
        btn.innerHTML = origHtml;
        lucide.createIcons();
        alert("Error reworking grouping.");
    });
});
"""
# insert before switchView
content = content.replace("function switchView(viewId)", rework_listener + "\nfunction switchView(viewId)")

# 3. Modify loadPlaces() and renderPlaces()
places_logic = """
// Load Places
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
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
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
        state.placesMapInstance.setView([20, 0], 2);
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
            const thumbUrl = `/api/thumbnail?path=${encodeURIComponent(firstMarkerData.path)}`;
            
            return L.divIcon({
                html: `
                    <div style="width: 50px; height: 50px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.3); background-image: url('${thumbUrl}'); background-size: cover; background-position: center; position: relative;">
                        <div style="position: absolute; bottom: -5px; right: -5px; background: var(--accent); color: white; border-radius: 12px; padding: 2px 6px; font-size: 11px; font-weight: bold;">
                            ${childCount}
                        </div>
                    </div>
                `,
                className: 'custom-cluster-icon',
                iconSize: L.point(50, 50)
            });
        }
    });
    
    const bounds = [];
    
    mapData.forEach(photo => {
        const marker = L.marker([photo.latitude, photo.longitude], { photoData: photo });
        
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
        state.placesMapInstance.fitBounds(bounds, { padding: [50, 50] });
    }, 300);
}

function renderPlaces(places) {
    if (!places || places.length === 0) {
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
    places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        
        // Beautiful background gradient styling
        let bgStyle = '';
        if (place.sample_path) {
            const thumbUrl = `/api/thumbnail?path=${encodeURIComponent(place.sample_path)}`;
            bgStyle = `background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%), url('${thumbUrl}'); background-size: cover; background-position: center; border: none; color: white; display: flex; flex-direction: column; justify-content: flex-end; padding: 16px; min-height: 180px; align-items: flex-start;`;
        }
        
        card.style = bgStyle;
        
        card.innerHTML = `
            <div style="z-index: 2; position: relative;">
                <h3 style="margin: 0; margin-bottom: 4px; color: white; font-size: 1.1rem;">${place.name}</h3>
                <span style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">${place.count} photos</span>
            </div>
        `;
        
        card.addEventListener('click', () => {
            state.filters.customPaths = null;
            state.filters.places = [place.name];
            applyFilters();
        });
        
        elements.placesGrid.appendChild(card);
    });
    
    lucide.createIcons();
}
"""

# Replace the existing loadPlaces and renderPlaces
start_idx = content.find("// Load Places")
end_idx = content.find("// Search Suggestions")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + places_logic + "\n" + content[end_idx:]
    
    # We also need to implement customPaths in applyFilters
    apply_logic = """
        if (state.filters.customPaths) {
            if (!state.filters.customPaths.includes(p.path)) {
                return false;
            }
        }
        
        // 1. Text Search
"""
    content = content.replace("// 1. Text Search", apply_logic)
    
    # Need to make sure customPaths is reset when clicking other nav items
    nav_reset = """
    // Reset customPaths when switching views
    state.filters.customPaths = null;
    
    // Handle specific views
"""
    content = content.replace("// Handle specific views", nav_reset)
    
    with codecs.open('static/app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("app.js patched successfully.")
else:
    print("Could not find markers.")
