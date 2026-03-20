self.addEventListener('install', (event) => {
    console.log('[Service Worker] Install');
});
self.addEventListener('fetch', (event) => {
    // Basic pass-through fetch for now
    event.respondWith(fetch(event.request));
});
