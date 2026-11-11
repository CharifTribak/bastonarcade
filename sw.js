// Baston Arcade service worker. It makes the site installable as an app, and it always goes to the network first:
// every page and file is fetched fresh from the server, so a new game or fix shows at the next launch. The copy it
// keeps is used only when there is no network at all, to open the home page instead of an error.
// To switch it off for everyone, publish this file with KILL = true: at the next launch it removes itself and its copy.
const KILL = false;
const CACHE = 'baston-v1';
const CORE = ['./', 'index.html', 'lib/en.js', 'manifest.webmanifest', 'img/icon-192.png'];

self.addEventListener('install', e => {
  self.skipWaiting();
  if (!KILL) e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).catch(() => {}));
});
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => KILL || k !== CACHE).map(k => caches.delete(k)));
    if (KILL){ await self.registration.unregister(); return; }
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', e => {
  if (KILL) return;
  const r = e.request;
  if (r.method !== 'GET') return;
  const url = new URL(r.url);
  if (url.origin !== location.origin) return;           // other sites (game servers, stats): untouched
  const page = r.mode === 'navigate';
  e.respondWith((async () => {
    try {
      // pages are revalidated with the server every time; other files follow the server's usual short cache
      const res = await fetch(r, page ? { cache:'no-cache' } : undefined);
      // the home page is kept under one key whatever its ?salon= or ?jeu=; other pages and files under their own address
      const home = page && (url.pathname === '/' || url.pathname.endsWith('/index.html'));
      if (res.ok && res.type === 'basic'){ const copy = res.clone(); caches.open(CACHE).then(c => c.put(home ? './' : r, copy)).catch(() => {}); }
      return res;
    } catch (err){
      const hit = (await caches.match(r, { ignoreSearch:page })) || (page ? await caches.match('./') : null);
      if (hit) return hit;
      throw err;
    }
  })());
});
