/* Oha! Fragen – Offline-Cache. Kein Tracking, keine Netzwerk-Calls nach außen. */
const CACHE = 'oha-v1';
const ASSETS = [
  './',
  'index.html',
  'questions.json',
  'manifest.json',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png',
  'icons/apple-touch-icon.png',
  'fonts/instrument-serif-normal-latin.woff2',
  'fonts/instrument-serif-normal-latin-ext.woff2',
  'fonts/instrument-serif-italic-latin.woff2',
  'fonts/instrument-serif-italic-latin-ext.woff2'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS.map(u => new Request(u, {cache: 'reload'}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;

  // Navigation: erst Netz, offline dann die App-Shell aus dem Cache
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).catch(() => caches.match('index.html', {ignoreSearch: true})
        .then(r => r || caches.match('./')))
    );
    return;
  }

  // Alles andere: cache-first, im Hintergrund auffrischen
  e.respondWith(
    caches.match(req, {ignoreSearch: true}).then(hit => {
      const fresh = fetch(req).then(res => {
        if (res && res.ok) caches.open(CACHE).then(c => c.put(req, res.clone()));
        return res;
      }).catch(() => hit);
      return hit || fresh;
    })
  );
});
