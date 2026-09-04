// static/js/api.js — Universal API Adapter
// Auto-detects pywebview bridge vs Flask HTTP and routes calls accordingly.
// In Flask mode (dev/browser), all calls fall through to existing fetch() logic.
// In bridge mode (pywebview .exe), calls go directly to Python without HTTP.

const API = {
    // Auto-detect: are we running inside pywebview with a bridge?
    get isBridge() {
        return false;
    },

    // ─── Photos ─────────────────────────────────────────────
    async getPhotos(filters = {}) {
        let url = `/api/photos?_t=${Date.now()}&sort=${filters.sort || 'date_desc'}`;
        if (filters.people && filters.people.length > 0)
            url += `&people=${filters.people.join(',')}`;
        if (filters.places && filters.places.length > 0)
            url += `&places=${encodeURIComponent(filters.places.join(','))}`;
        if (filters.albums && filters.albums.length > 0)
            url += `&albums=${filters.albums.join(',')}`;
        if (filters.types && filters.types.length > 0)
            url += `&types=${filters.types.join(',')}`;
        if (filters.search)
            url += `&search=${encodeURIComponent(filters.search)}`;
        if (filters.date_query) {
            const dq = Array.isArray(filters.date_query)
                ? filters.date_query.join(',')
                : filters.date_query;
            if (dq) url += `&date_query=${encodeURIComponent(dq)}`;
        }
        if (filters.archived)  url += '&archived=true';
        if (filters.favorites) url += '&favorites=true';
        if (filters.trashed)   url += '&trashed=true';
        if (filters.smart === false) url += '&smart=false';
        if (filters.year) url += `&year=${filters.year}`;
        if (filters.month) url += `&month=${filters.month}`;
        const res = await fetch(url);
        return res.json();
    },

    // ─── People ─────────────────────────────────────────────
    async getPeople() {
        const res = await fetch('/api/people');
        return res.json();
    },

    // ─── Albums ─────────────────────────────────────────────
    async getAlbums() {
        const res = await fetch('/api/albums');
        return res.json();
    },

    // ─── Places ─────────────────────────────────────────────
    async getPlaces() {
        const res = await fetch('/api/places');
        return res.json();
    },

    // ─── Places Map Data ────────────────────────────────────
    async getPlacesMapData() {
        const res = await fetch('/api/places/map_data');
        return res.json();
    },

    // ─── Stats ──────────────────────────────────────────────
    async getStats() {
        const res = await fetch('/api/stats');
        return res.json();
    },

    // ─── Scan Status ──────────────────────────────────────────
    async getScanStatus() {
        const res = await fetch('/api/scan/status?t=' + Date.now());
        return res.json();
    },

    // ─── WRITE: Albums ─────────────────────────────────────────
    async createAlbum(name) {
        return (await fetch('/api/albums/create', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) })).json();
    },
    async addToAlbum(albumId, photos) {
        return (await fetch('/api/albums/add', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ album_id: albumId, photos }) })).json();
    },
    async removeFromAlbum(albumId, photos) {
        return (await fetch('/api/albums/remove', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ album_id: albumId, photos }) })).json();
    },
    async deleteAlbum(albumId) {
        return (await fetch('/api/albums/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ album_id: albumId }) })).json();
    },
    async renameAlbum(albumId, newName) {
        return (await fetch('/api/albums/rename', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ album_id: albumId, new_name: newName }) })).json();
    },
    async setAlbumCover(albumId, photoPath) {
        return (await fetch('/api/albums/set-cover', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ album_id: albumId, photo_path: photoPath }) })).json();
    },

    // ─── WRITE: Rename Person ──────────────────────────────────
    async renamePerson(personId, newName) {
        const res = await fetch('/api/people/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: personId, name: newName })
        });
        return res.json();
    },

    // ─── WRITE: Toggle Favorite ────────────────────────────────
    async toggleFavorite(photoPath) {
        const res = await fetch('/api/photo/favorite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: photoPath })
        });
        return res.json();
    },

    // ─── WRITE: Trash ──────────────────────────────────────────
    async moveToTrash(photos) {
        return (await fetch('/api/trash/move', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ photos }) })).json();
    },
    async restoreFromTrash(photos) {
        return (await fetch('/api/trash/restore', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ photos }) })).json();
    },
    async purgeTrash(photos) {
        return (await fetch('/api/trash/purge', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ photos }) })).json();
    },

    // ─── Thumbnails (always HTTP for now — Phase 4 will use file://) ──
    getThumbnailUrl(photoPath) {
        return `/api/photo/thumbnail/${encodeURIComponent(photoPath)}`;
    },

    getFaceCropUrl(faceId) {
        return `/api/photo/crop/${faceId}`;
    }
};
