---
layout: compress
permalink: '/sw.js'
# PWA service worker
---

self.importScripts('{{ "/assets/js/data/swcache.js" | relative_url }}');

const cacheName = 'chirpy-{{ "now" | date: "%s" }}';

function verifyDomain(url) {
  for (const domain of allowedDomains) {
    const regex = RegExp(`^http(s)?:\/\/${domain}\/`);
    if (regex.test(url)) {
      return true;
    }
  }

  return false;
}

function isGamePath(url) {
  const path = new URL(url).pathname;
  return gamePaths.some((p) => path.startsWith(p));
}

function isExcluded(url) {
  for (const item of denyUrls) {
    if (url === item) {
      return true;
    }
  }
  return false;
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(cacheName).then((cache) => {
      return cache.addAll(resource);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== cacheName) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  /* 게임 경로는 respondWith를 호출하지 않아 브라우저가 평소대로 네트워크에서 받게 한다 */
  if (isGamePath(event.request.url)) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }

      return fetch(event.request).then((response) => {
        const url = event.request.url;

        /* 실패 응답(404 등)은 캐시하지 않는다. 캐시하면 원인이 해결된 뒤에도 같은 오류가 계속 보인다.
           단, 교차 출처 opaque 응답(status 0)은 상태를 알 수 없어 response.ok가 항상 false이므로
           same-origin(basic) 응답에 한해서만 이 검사를 적용한다 */
        if (
          (response.type === 'basic' && !response.ok) ||
          event.request.method !== 'GET' ||
          !verifyDomain(url) ||
          isExcluded(url)
        ) {
          return response;
        }

        /* see: <https://developers.google.com/web/fundamentals/primers/service-workers#cache_and_return_requests> */
        let responseToCache = response.clone();

        caches.open(cacheName).then((cache) => {
          /* console.log('[sw] Caching new resource: ' + event.request.url); */
          cache.put(event.request, responseToCache);
        });

        return response;
      });
    })
  );
});
