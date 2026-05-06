// Overview network — entry point.
// Phase 3: graph render. Phase 4: filters + URL state. Phase 5: search + list.
import { initFilters } from './filters.js';
import { initSearch }  from './search.js';

const GRAPH_URL  = new URL('graph.json', document.baseURI).toString();
const LAYOUT_KEY = 'ov-layout-v3';     // bumped: invalidate the collapsed-line layout

const TOPIC_VAR = ['--ov-t1','--ov-t2','--ov-t3','--ov-t4','--ov-t5','--ov-t6','--ov-t7','--ov-t8'];

function cssVar(name) {
  // Read from <body> so values cascaded from body.colorscheme-{light,dark}
  // resolve to the active scheme — :root only sees the light defaults.
  const el = document.body || document.documentElement;
  return getComputedStyle(el).getPropertyValue(name).trim() || '#888';
}

function topicColour(slug, topicIndex) {
  const i = topicIndex.get(slug);
  if (i == null) return cssVar('--ov-text-2');
  return cssVar(TOPIC_VAR[(i - 1) % TOPIC_VAR.length]);
}

function shapeFor(type) {
  return type === 'publication' ? 'ellipse'
       : type === 'software'    ? 'round-rectangle'
                                : 'triangle';
}

function buildElements(graph, topicIndex) {
  const nodes = [];
  for (const n of graph.nodes) {
    const colour = topicColour(n.primary_topic, topicIndex);
    nodes.push({
      data: {
        id: n.id,
        label: n.title,
        type: n.type,
        url: n.url,
        year: n.year || null,
        venue: n.venue || null,
        authors: n.authors || null,
        description: n.description || null,
        primary_topic: n.primary_topic,
        colour,
      },
      classes: n.type,
    });
  }

  const edges = graph.edges.map((e, i) => ({
    data: { id: `e${i}`, source: e.source, target: e.target, kind: e.kind, weight: e.weight },
    classes: e.kind,
  }));

  return { nodes, edges };
}

function styleSheet() {
  return [
    {
      selector: 'node',
      style: {
        'background-color': 'data(colour)',
        'border-color': 'data(colour)',
        'border-width': 0,
        'label': '',
        'width': 14,
        'height': 14,
      },
    },
    { selector: 'node.publication', style: { 'shape': 'ellipse', 'width': 14, 'height': 14 } },
    { selector: 'node.software',    style: { 'shape': 'round-rectangle', 'width': 14, 'height': 14 } },
    {
      selector: 'edge',
      style: {
        'curve-style': 'haystack',
        'width': 0.8,
        'line-color': cssVar('--ov-edge'),
        'opacity': 0.55,
      },
    },
    {
      selector: 'edge.topic-related',
      style: {
        'line-style': 'dashed',
        'line-color': cssVar('--ov-edge'),
        'opacity': 0.35,
        'width': 0.8,
      },
    },
    {
      selector: 'edge.shared-tags',
      style: {
        'line-style': 'solid',
        'line-color': cssVar('--ov-edge'),
        'opacity': 0.75,
        'width': 'mapData(weight, 1, 5, 1, 3)',
      },
    },
    {
      selector: 'edge.used-in',
      style: {
        'curve-style': 'bezier',
        'line-style': 'solid',
        'opacity': 0.95,
        'width': 2.5,
        'target-arrow-shape': 'triangle',
        'target-arrow-color': cssVar('--ov-edge'),
        'line-color': cssVar('--ov-edge'),
      },
    },
    {
      selector: 'node:active, node.hover',
      style: {
        'border-width': 2,
        'border-color': cssVar('--ov-highlight'),
      },
    },
  ];
}

function showTooltip(el, evt) {
  const tip = document.getElementById('ov-tooltip');
  const d = el.data();
  let html = `<div style="font-weight:600;line-height:1.3;margin-bottom:.25rem;">${escapeHtml(d.label)}</div>`;
  if (d.type === 'publication') {
    html += `<div style="color:var(--ov-text-2);font-size:.75rem;line-height:1.35;margin-bottom:.2rem;">${escapeHtml(d.authors || '')}</div>`;
    html += `<div style="font-size:.75rem;"><em>${escapeHtml(d.venue || '')}</em> · ${d.year ?? ''}</div>`;
  } else if (d.type === 'software') {
    html += `<div style="color:var(--ov-text-2);font-size:.75rem;line-height:1.35;">${escapeHtml(d.description || '')}</div>`;
  }
  if (d.url) {
    const which = d.type === 'publication' ? 'DOI' : 'GitHub';
    html += `<div style="margin-top:.35rem;font-size:.7rem;color:var(--link-color, #3D5A80);">Click to open ${which} ↗</div>`;
  }
  tip.innerHTML = html;
  const cont = document.querySelector('.ov-graph').getBoundingClientRect();
  const x = (evt.originalEvent?.clientX ?? cont.left + cont.width / 2) - cont.left + 12;
  const y = (evt.originalEvent?.clientY ?? cont.top + cont.height / 2) - cont.top + 12;
  tip.style.left = `${x}px`;
  tip.style.top = `${y}px`;
  tip.style.opacity = '1';
}

function hideTooltip() {
  const tip = document.getElementById('ov-tooltip');
  if (tip) tip.style.opacity = '0';
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function persistLayout(cy) {
  const positions = {};
  cy.nodes().forEach(n => {
    const p = n.position();
    positions[n.id()] = { x: Math.round(p.x), y: Math.round(p.y) };
  });
  try { localStorage.setItem(LAYOUT_KEY, JSON.stringify(positions)); }
  catch { /* localStorage may be full or disabled — ignore */ }
}

function readLayoutCache() {
  try {
    const raw = localStorage.getItem(LAYOUT_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

function topicIndexFromGraph(graph) {
  const m = new Map();
  graph.topics.research.forEach(t => m.set(t.slug, t.colour_index));
  return m;
}

function loadScript(src, integrity) {
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = src; s.async = false;
    if (integrity) { s.integrity = integrity; s.crossOrigin = 'anonymous'; }
    s.onload = resolve;
    s.onerror = () => reject(new Error(`failed to load ${src}`));
    document.head.append(s);
  });
}

const CDN = [
  ['https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js', 'sha384-H3uzGzTfGHUAumB8+s4GEdfFwzAceN9wCCndN8AXubWKFIPuBSWKKtWDx7RhSf/z'],
  ['https://unpkg.com/layout-base@2.0.1/layout-base.js',       'sha384-5E2lB9AIGE6LRCnOOSTnZRlYZFZ01iMeN2fw97Z1r4Z/kXALxKw2AC+ZzQqoeDsG'],
  ['https://unpkg.com/cose-base@2.2.0/cose-base.js',           'sha384-RswRBkrMsPUYpJLbZ1CVA08zbNzAkykE2oGJTujBwfjWNdfxv2WVjLJNqv1LhAOp'],
  ['https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js','sha384-uk5Wbjq1+KqUdHO30w7N7GrEGdzBhaJeW9o/ANF6v9+yx3M/cBmoX51C000JNCUf'],
];

const isMobile = window.matchMedia('(max-width: 767px)').matches;

async function init() {
  const cyContainer = document.getElementById('ov-cy');
  const loading = document.getElementById('ov-loading');

  let graph;
  try {
    const r = await fetch(GRAPH_URL);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    graph = await r.json();
  } catch (e) {
    if (loading) loading.textContent = `failed to load graph (${e.message})`;
    return;
  }

  const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setText('ov-stat-pub',    graph.stats.publications);
  setText('ov-stat-sw',     graph.stats.software);
  const edgesEl = document.getElementById('ov-stat-edges');
  if (edgesEl) edgesEl.textContent =
    `${graph.stats.edges_total} edges · ${(graph.stats.coverage * 100).toFixed(0)}% coverage`;

  // Mobile: skip Cytoscape entirely; list + search + filters still work.
  if (isMobile) {
    if (loading) loading.textContent = 'graph hidden on small screens';
    initSearch({ graph });
    initFilters({ graph, cy: stubCy(), store: null });
    return;
  }

  // Desktop: load Cytoscape from CDN, then proceed.
  try {
    for (const [url, integrity] of CDN) await loadScript(url, integrity);
  } catch (e) {
    if (loading) loading.textContent = `failed to load Cytoscape (${e.message})`;
    return;
  }

  const topicIndex = topicIndexFromGraph(graph);
  const { nodes, edges } = buildElements(graph, topicIndex);

  const cached = readLayoutCache();
  const useCached = cached && nodes.every(n => n.data.id in cached);

  const cy = cytoscape({
    container: cyContainer,
    elements: { nodes, edges },
    style: styleSheet(),
    minZoom: 0.2,
    maxZoom: 4,
    wheelSensitivity: 0.25,
    layout: useCached
      ? {
          name: 'preset',
          positions: id => cached[id],
          fit: true,
          padding: 20,
        }
      : {
          name: 'fcose',
          quality: 'proof',
          randomize: true,
          animate: false,
          nodeRepulsion: 9000,
          idealEdgeLength: 90,
          edgeElasticity: 0.25,
          gravity: 0.4,
          gravityRange: 1.6,
          gravityCompound: 1.0,
          numIter: 3500,
          tile: true,
          packComponents: true,
          tilingPaddingVertical: 30,
          tilingPaddingHorizontal: 30,
          padding: 40,
          fit: true,
        },
  });

  cy.ready(() => {
    loading.style.display = 'none';
    if (!useCached) persistLayout(cy);
    initSearch({ graph });
    initFilters({ graph, cy, store: null });
  });

  cy.on('mouseover', 'node', (evt) => showTooltip(evt.target, evt));
  cy.on('mousemove', 'node', (evt) => showTooltip(evt.target, evt));
  cy.on('mouseout',  'node', () => hideTooltip());

  cy.on('tap', 'node', (evt) => {
    const url = evt.target.data('url');
    if (url) window.open(url, '_blank', 'noopener');
  });

  // Re-style on Coder theme toggle (body class flips between colorscheme-light / -dark).
  const restyle = () => cy.style(styleSheet());
  const observer = new MutationObserver(restyle);
  observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
  // Also re-style if the OS scheme flips while in colorscheme-auto.
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', restyle);
}

function stubCy() {
  const empty = { forEach() {}, addClass() {}, removeClass() {}, nonempty: () => false };
  return {
    batch(fn) { fn(); },
    nodes() { return Object.assign(empty, { style() {} }); },
    edges() { return Object.assign(empty, { style() {} }); },
    getElementById() { return empty; },
    on() {},
  };
}

init();
