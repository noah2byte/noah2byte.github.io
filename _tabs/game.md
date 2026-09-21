---
title: 게임
icon: fas fa-gamepad
order: 6
permalink: /game/
---

만든 게임들을 모아두는 페이지입니다.

{% comment %}
  카드를 누르면 페이지를 떠나지 않고 이 탭 안의 플레이어(dialog)에서 게임을 연다.
  - 카드는 게임 주소를 가리키는 <a>라서 JS가 없거나 Ctrl/⌘+클릭하면 새 탭으로 그대로 열린다(점진적 향상)
  - /game/#city-rush 처럼 id를 붙이면 해당 게임이 바로 열린다(id가 없으면 url의 마지막 경로). 블로그 글에서는 게임을 임베드하지 않고 이 주소로 링크한다
  - 플레이어를 닫으면 iframe을 제거한다. WebGL 게임은 떠 있는 동안 계속 GPU를 쓰기 때문이다
  - 아래 HTML 전체를 {::nomarkdown}으로 감싼다. kramdown은 빈 줄이 없거나 들여쓴 HTML을 마크다운 문단으로 해석해
    태그가 글자로 노출되므로, 마크다운 변환에서 통째로 제외하는 편이 확실하다.
    같은 이유로 Liquid 공백 제거 문법(태그 괄호 안쪽의 하이픈)은 블록 경계의 빈 줄을 지울 수 있어 쓰지 않는다
{% endcomment %}

{::nomarkdown}

<div class="game-grid">
{% for game in site.data.games %}
  {% comment %} id가 없는 기존 항목은 url의 마지막 경로를 id로 쓴다(…/world-bomb-war-game/ → world-bomb-war-game) {% endcomment %}
  {% comment %} split 결과 끝의 빈 문자열 처리가 Liquid 구현마다 달라, 비어 있지 않은 마지막 조각을 직접 찾는다 {% endcomment %}
  {% assign gid = "" %}
  {% assign parts = game.url | split: "/" %}
  {% for part in parts %}{% if part != "" %}{% assign gid = part %}{% endif %}{% endfor %}
  {% if game.id %}{% assign gid = game.id %}{% endif %}
  <a class="game-card" id="{{ gid }}" href="{{ game.url }}" target="_blank" rel="noopener"
     data-game-id="{{ gid }}" data-game-title="{{ game.title }}" data-game-source="{{ game.source }}">
    {% if game.thumbnail %}
    {% comment %}
      썸네일은 img 태그가 아닌 배경 이미지로 넣는다. Chirpy(_includes/refactor-content.html)는 본문의 모든 img를
      이미지 확대용 a 태그로 감싸고 class를 떼어낸다. 카드(a) 안에 a가 또 생기면 브라우저가 카드를 둘로 쪼개
      썸네일만 따로 눌리고(이미지 확대) 카드 영역이 어긋난다
    {% endcomment %}
    <div class="game-thumb" role="img" aria-label="{{ game.title }} 플레이 화면" style="background-image: url('{{ game.thumbnail | relative_url }}')"></div>
    {% else %}
    {% comment %} 썸네일이 없어도 카드 높이·모양이 맞도록 같은 비율의 기본 커버를 둔다 {% endcomment %}
    <div class="game-thumb game-cover" aria-hidden="true">{{ game.icon | default: "🎮" }}</div>
    {% endif %}
    <div class="game-body">
      <div class="game-category">{{ game.category | default: "Web Game" }}</div>
      <div class="game-title">{{ game.icon | default: "🎮" }} {{ game.title }}</div>
      <div class="game-desc">{{ game.description }}</div>
      {% if game.controls %}
      <div class="game-controls">{{ game.controls }}</div>
      {% endif %}
      <div class="game-play">▶ 플레이</div>
    </div>
  </a>
{% endfor %}
</div>

<dialog id="game-player" aria-labelledby="game-player-title">
  <div class="gp-bar">
    <strong id="game-player-title" class="gp-title"></strong>
    <span class="gp-actions">
      <button type="button" class="gp-full">전체 화면</button>
      <a class="gp-source" href="#" target="_blank" rel="noopener">소스</a>
      <a class="gp-newtab" href="#" target="_blank" rel="noopener">새 탭</a>
      <button type="button" class="gp-close" aria-label="닫기">✕</button>
    </span>
  </div>
  <div class="gp-frame"></div>
</dialog>

<style>
  .game-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-top: 1rem; }
  .game-card {
    display: flex; flex-direction: column; border-radius: 16px; overflow: hidden;
    border: 1px solid #e2e8f0 !important; /* Chirpy 본문 링크 밑줄(border-bottom)을 덮어쓴다 */
    background: linear-gradient(135deg, #f0f4ff 0%, #fafafa 100%);
    text-decoration: none !important;
    transition: transform .15s, box-shadow .15s;
  }
  .game-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99, 102, 241, .18); }
  .game-card:focus-visible { outline: 3px solid #6366f1; outline-offset: 2px; }
  .game-thumb { display: block; width: 100%; aspect-ratio: 16 / 10; background-size: cover; background-position: center; }
  .game-body { padding: 18px 20px 20px; display: flex; flex-direction: column; flex: 1; }
  .game-cover {
    display: flex; align-items: center; justify-content: center; font-size: 56px;
    background: radial-gradient(circle at 50% 40%, #e0e7ff, #c7d2fe);
  }
  .game-category { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #6366f1; margin-bottom: 6px; }
  .game-title { font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
  .game-desc { font-size: 13px; color: #64748b; line-height: 1.55; }
  .game-controls { font-size: 12px; color: #94a3b8; margin-top: 8px; }
  .game-play { margin-top: auto; padding-top: 14px; font-size: 13px; font-weight: 700; color: #6366f1; }

  /* 다크 모드: Chirpy는 토글하면 html[data-mode]를 쓰고, 토글 전에는 시스템 설정을 따른다.
     기존 카드는 밝은 색이 고정이라 다크 모드에서 카드만 하얗게 튀었다 */
  html[data-mode="dark"] .game-card { border-color: #2d3348 !important; background: linear-gradient(135deg, #1e2233 0%, #171a26 100%); }
  html[data-mode="dark"] .game-title { color: #e2e8f0; }
  html[data-mode="dark"] .game-cover { background: radial-gradient(circle at 50% 40%, #2b3150, #1a1e30); }
  html[data-mode="dark"] .game-desc { color: #a0aec0; }
  html[data-mode="dark"] .game-category, html[data-mode="dark"] .game-play { color: #a5b4fc; }
  @media (prefers-color-scheme: dark) {
    html:not([data-mode]) .game-card { border-color: #2d3348 !important; background: linear-gradient(135deg, #1e2233 0%, #171a26 100%); }
    html:not([data-mode]) .game-title { color: #e2e8f0; }
    html:not([data-mode]) .game-cover { background: radial-gradient(circle at 50% 40%, #2b3150, #1a1e30); }
    html:not([data-mode]) .game-desc { color: #a0aec0; }
    html:not([data-mode]) .game-category, html:not([data-mode]) .game-play { color: #a5b4fc; }
  }

  #game-player {
    width: min(1100px, 96vw); max-width: none; height: min(720px, 90vh); max-height: none;
    padding: 0; border: 0; border-radius: 14px; overflow: hidden; background: #0f1220; color: #e8eaf6;
  }
  #game-player[open] { display: flex; flex-direction: column; }
  #game-player::backdrop { background: rgba(5, 8, 20, .72); backdrop-filter: blur(3px); }
  .gp-bar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 14px; }
  .gp-actions { display: flex; align-items: center; gap: 8px; }
  .gp-actions button, .gp-actions a {
    font: inherit; font-size: .85rem; color: inherit !important; background: rgba(255, 255, 255, .08);
    border: 0 !important; border-radius: 8px; padding: 6px 10px; cursor: pointer; text-decoration: none !important;
  }
  .gp-actions button:hover, .gp-actions a:hover { background: rgba(255, 255, 255, .16); }
  .gp-actions [hidden] { display: none; }
  .gp-frame { flex: 1; min-height: 0; }
  .gp-frame iframe { display: block; width: 100%; height: 100%; border: 0; }
  /* 모바일은 화면 전체를 쓴다. 게임 영역이 작아지면 터치 조향이 불편하다 */
  @media (max-width: 576px) {
    #game-player { width: 100vw; height: 100dvh; border-radius: 0; }
  }
</style>

<script>
  (() => {
    const dialog = document.getElementById('game-player');
    if (!dialog || typeof dialog.showModal !== 'function') return; /* dialog 미지원 브라우저는 카드 링크(새 탭)로 동작한다 */
    const frame = dialog.querySelector('.gp-frame');
    const title = dialog.querySelector('.gp-title');
    const newTab = dialog.querySelector('.gp-newtab');
    const source = dialog.querySelector('.gp-source');
    const cards = [...document.querySelectorAll('.game-card')];

    function open(card) {
      const iframe = document.createElement('iframe');
      iframe.src = card.href;
      iframe.title = card.dataset.gameTitle;
      iframe.allow = 'fullscreen; gamepad';
      frame.replaceChildren(iframe);
      title.textContent = card.dataset.gameTitle;
      newTab.href = card.href;
      source.hidden = !card.dataset.gameSource;
      if (card.dataset.gameSource) source.href = card.dataset.gameSource;
      dialog.showModal();
      iframe.focus(); /* 키보드 입력이 바로 게임으로 가도록 */
      /* 주소에 게임 id를 남겨 그대로 공유·새로고침해도 같은 게임이 열리게 한다 */
      history.replaceState(null, '', `#${card.dataset.gameId}`);
    }

    /* 정리는 닫는 즉시 동기로 한다. close 이벤트는 비동기로 전달돼, 무거운 게임이 메인 스레드를 잡고 있으면 늦게 처리된다 */
    function cleanup() {
      if (!frame.firstChild) return;
      frame.replaceChildren(); /* iframe을 지워 게임 루프와 GPU 사용을 멈춘다 */
      history.replaceState(null, '', location.pathname + location.search);
    }
    function close() {
      dialog.close();
      cleanup();
    }
    dialog.addEventListener('close', cleanup); /* ESC로 닫는 경우 */
    dialog.addEventListener('click', e => { if (e.target === dialog) close(); }); /* 바깥(backdrop) 클릭으로 닫기 */
    dialog.querySelector('.gp-close').addEventListener('click', close);
    dialog.querySelector('.gp-full').addEventListener('click', () => frame.querySelector('iframe')?.requestFullscreen?.());

    for (const card of cards) {
      card.addEventListener('click', e => {
        if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return; /* 새 탭 열기 동작은 그대로 둔다 */
        e.preventDefault();
        open(card);
      });
    }

    const initial = cards.find(c => `#${c.dataset.gameId}` === location.hash);
    if (initial) open(initial);
  })();
</script>
{:/nomarkdown}