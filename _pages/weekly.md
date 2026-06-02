---
layout: page
title: Weekly Digest
permalink: /weekly/
---

<div class="card mt-4">
  <div class="card-body">

    <h3>📰 Weekly Digest</h3>

    <details>
      <summary>GeekNews Weekly</summary>
      <ul>
        {% for item in site.data.weekly.geeknews %}
        <li>
          <a href="{{ item.url }}">{{ item.title }}</a>
        </li>
        {% endfor %}
      </ul>
    </details>

    <details class="mt-3">
      <summary>요즘IT Weekly</summary>
      <ul>
        <ul>
          {% for item in site.data.weekly.yozmit %}
          <li>
            <a href="{{ item.url }}">{{ item.title }}</a>
          </li>
          {% endfor %}
        </ul>
      </ul>
    </details>

  </div>
</div>
