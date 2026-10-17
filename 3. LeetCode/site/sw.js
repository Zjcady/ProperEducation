// Study Coach service worker: the page shell works offline; data.json is always fetched fresh
// when there's a network, and the last copy is shown when there isn't.
const SHELL = "coach-shell-v1";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "apple-touch-icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== SHELL && k !== "coach-data").map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  if (url.pathname.endsWith("/data.json")) {
    // network first, fall back to the last good copy
    e.respondWith(fetch(e.request, { cache: "no-store" })
      .then(r => { const copy = r.clone(); caches.open("coach-data").then(c => c.put("data.json", copy)); return r; })
      .catch(() => caches.open("coach-data").then(c => c.match("data.json"))));
    return;
  }
  // page shell: cache first, refresh in the background
  e.respondWith(caches.match(e.request).then(hit => {
    const net = fetch(e.request).then(r => { if (r.ok) caches.open(SHELL).then(c => c.put(e.request, r.clone())); return r; }).catch(() => hit);
    return hit || net;
  }));
});
