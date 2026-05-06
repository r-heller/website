---
title: "Overview"
date: 2026-05-06
description: "Discovery network across publications and software."
---

A discovery network spanning publications and software. Hover a node to
inspect; click to follow. On small screens the graph is hidden — the
filtered list below is the canonical view.

<div id="ov-app" class="ov-page">
  <div class="ov-header">
    <input id="ov-search" class="ov-search" type="text"
           placeholder="Search publications and software…" disabled>
    <div id="ov-type-chips" class="ov-type-chips" aria-hidden="true">
      <button class="ov-chip" type="button" disabled>● Publications</button>
      <button class="ov-chip" type="button" disabled>■ Software</button>
    </div>
  </div>
  <div class="ov-body">
    <aside class="ov-rail" aria-label="Filters">
      <div id="ov-rail-body"></div>
    </aside>
    <section class="ov-graph" aria-label="Network graph">
      <div id="ov-cy" style="position:absolute; inset:0;"></div>
      <div id="ov-loading" class="placeholder">loading…</div>
      <div id="ov-tooltip" role="tooltip" aria-hidden="true"
           style="position:absolute; pointer-events:none; opacity:0; transition:opacity 120ms;
                  background:var(--ov-surface); border:1px solid var(--ov-border);
                  border-radius:6px; padding:.45rem .6rem; font-size:.8rem;
                  max-width:280px; box-shadow:0 4px 12px rgba(0,0,0,.08); z-index:5;"></div>
    </section>
  </div>
  <div class="ov-stats">
    <span><strong id="ov-stat-pub">…</strong> publications</span>
    <span><strong id="ov-stat-sw">…</strong> software</span>
    <span style="margin-left:auto;font-family:var(--ov-mono);" id="ov-stat-edges">…</span>
  </div>
  <nav class="ov-lists ov-lists-2col" aria-label="All works">
    <section id="ov-col-pub" class="ov-col" aria-labelledby="ov-col-pub-heading">
      <h3 id="ov-col-pub-heading">Publications <span class="count" id="ov-col-count-pub">…</span></h3>
      <div class="ov-col-cards"></div>
    </section>
    <section id="ov-col-sw" class="ov-col" aria-labelledby="ov-col-sw-heading">
      <h3 id="ov-col-sw-heading">Software <span class="count" id="ov-col-count-sw">…</span></h3>
      <div class="ov-col-cards"></div>
    </section>
  </nav>
</div>

<script type="module" src="/website/js/overview/main.js"></script>
