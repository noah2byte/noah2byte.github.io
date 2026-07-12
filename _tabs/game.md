---
title: 게임
icon: fas fa-gamepad
order: 6
permalink: /game/
---

만든 게임들을 모아두는 페이지입니다.

<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px;">
  {% for game in site.data.games %}
  <a href="{{ game.url }}" target="_blank" rel="noopener"
     style="display: block; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; background: linear-gradient(135deg, #f0f4ff 0%, #fafafa 100%); padding: 20px; text-decoration: none;">
    <div style="font-size: 28px; margin-bottom: 8px;">{{ game.icon | default: "🎮" }}</div>
    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #6366f1; margin-bottom: 6px;">
      {{ game.category | default: "Web Game" }}
    </div>
    <div style="font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 4px;">
      {{ game.title }}
    </div>
    <div style="font-size: 13px; color: #64748b;">
      {{ game.description }}
    </div>
  </a>
  {% endfor %}
</div>
