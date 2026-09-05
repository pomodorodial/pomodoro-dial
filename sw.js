/* Pomodoro Dial service worker: makes the app work offline.
   Pages are fetched network-first (so updates arrive immediately) with the cached copy as fallback.
   Fonts, icons and other files are served from cache and refreshed in the background. */
const VERSION = 'pomodoro-dial-v2';
const PRECACHE = [
  './', 'index.html', 'site.css', 'manifest.webmanifest', 'favicon.svg', 'icon-192.png', 'icon-512.png',
  'fonts/azeret-mono-latin.woff2', 'fonts/azeret-mono-latin-ext.woff2',
  'fonts/instrument-sans-latin.woff2', 'fonts/instrument-sans-latin-ext.woff2'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(VERSION).then(cache => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;           // analytics beacon etc. go straight to the network

  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).then(res => {
        if (res.ok) caches.open(VERSION).then(cache => cache.put(req, res.clone()));
        return res;
      }).catch(() => caches.match(req).then(hit => hit || caches.match('./')).then(hit => hit || caches.match('index.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(req).then(cached => {
      const fromNetwork = fetch(req).then(res => {
        if (res.ok) caches.open(VERSION).then(cache => cache.put(req, res.clone()));
        return res;
      }).catch(() => cached);
      return cached || fromNetwork;
    })
  );
});
