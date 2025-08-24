self.addEventListener('install', function(e) {
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  self.clients.claim();
});

self.addEventListener('fetch', function(event) {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(function() {
        return caches.open('samms-static-v1').then(function(cache) {
          return cache.match('/static/offline.html');
        });
      })
    );
    return;
  }
  // Estrategia simple: solo cachea archivos estáticos
  if (event.request.url.includes('/static/')) {
    event.respondWith(
      caches.open('samms-static-v1').then(function(cache) {
        return cache.match(event.request).then(function (response) {
          return response || fetch(event.request).then(function(response) {
            cache.put(event.request, response.clone());
            return response;
          });
        });
      })
    );
  }
});
