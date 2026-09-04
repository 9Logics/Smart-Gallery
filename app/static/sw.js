
const CACHE_NAME = 'gallery-cache-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  // A minimal pass-through fetch handler is required by some browsers for PWA installability.
  event.respondWith(fetch(event.request));
});
