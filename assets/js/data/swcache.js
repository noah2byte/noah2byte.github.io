---
layout: compress
# The list to be cached by PWA
---

const resource = [
  /* --- CSS --- */
  '{{ "/assets/css/:THEME.css" | replace: ':THEME', site.theme | relative_url }}',

  /* --- PWA --- */
  '{{ "/app.js" | relative_url }}',
  '{{ "/sw.js" | relative_url }}',

  /* --- HTML --- */
  '{{ "/index.html" | relative_url }}',
  '{{ "/404.html" | relative_url }}',

  {% for tab in site.tabs %}
    '{{ tab.url | relative_url }}',
  {% endfor %}

  /* --- Favicons & compressed JS --- */
  {% assign cache_list = site.static_files | where: 'swcache', true  %}
  {% for file in cache_list %}
    '{{ file.path | relative_url }}'{%- unless forloop.last -%},{%- endunless -%}
  {% endfor %}
];

/* The request url with below domain will be cached */
const allowedDomains = [
  {% if site.google_analytics.id != empty and site.google_analytics.id %}
    'www.googletagmanager.com',
    'www.google-analytics.com',
  {% endif %}

  '{{ site.url | split: "//" | last }}',

  {% if site.img_cdn contains '//' and site.img_cdn %}
    '{{ site.img_cdn | split: '//' | last | split: '/' | first }}',
  {% endif %}

  'fonts.gstatic.com',
  'fonts.googleapis.com',
  'cdn.jsdelivr.net',
  'polyfill.io'
];

/* Requests that include the following path will be banned */
const denyUrls = [];

/* 게임 경로: 서비스 워커가 가로채지 않고 항상 네트워크로 보낸다.
   게임은 블로그와 별도 저장소로 같은 도메인 하위 경로(/paper-boat/ 등)에 배포된다.
   블로그 서비스 워커의 관할 범위(/)에 포함되므로, 가로채면 배포 전 404나 옛 버전이 캐시에 남아 계속 보인다.
   목록은 _data/games.yml에서 자동으로 만든다. 게임을 추가해도 이 파일은 고칠 필요가 없다 */
const gamePaths = [
  {% for game in site.data.games %}
    {% if game.url contains site.url %}
      '{{ game.url | remove_first: site.url }}',
    {% endif %}
  {% endfor %}
];
