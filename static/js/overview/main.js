// Overview network — entry point.
// Phase 3: graph render. Phase 4: filters + URL state. Phase 5: search + list.
import { initFilters } from './filters.js';
import { initSearch }  from './search.js';
import { initList }    from './list.js';

const GRAPH_URL  = new URL('graph.json', document.baseURI).toString();
const LAYOUT_KEY = 'ov-layout-v1';     // localStorage key (Phase 3 caches client-side)
const ZOOM_THRESHOLD = 1.5;            // below: course leaves hidden, parent visible

const TOPIC_VAR = ['--ov-t1','--ov-t2','--ov-t3','--ov-t4','--ov-t5','--ov-t6','--ov-t7','--ov-t8'];

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '#888';
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
  const compoundIds = new Set();

  // course compound parents — one per tutorial-topic.
  for (const t of graph.topics.tutorial) {
    const parentId = `parent-${t.slug}`;
    compoundIds.add(parentId);
    nodes.push({
      data: {
        id: parentId,
        label: t.label,
        type: 'compound',
        primary_topic: t.slug,
        colour: cssVar('--ov-text-2'),
      },
      classes: 'compound',
    });
  }

  for (const n of graph.nodes) {
    const colour = topicColour(n.primary_topic, topicIndex);
    const data = {
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
    };
    if (n.type === 'course') data.parent = `parent-${n.tutorial_topic}`;
    nodes.push({ data, classes: n.type });
  }

  const edges = graph.edges.map((e, i) => ({
    data: { id: `e${i}`, source: e.source, target: e.target, kind: e.kind, weight: e.weight },
    classes: e.kind,
  }));

  return { nodes, edges, compoundIds };
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
    { selector: 'node.course',      style: { 'shape': 'triangle', 'width': 12, 'height': 12 } },
    {
      selector: 'node.compound',
      style: {
        'shape': 'round-rectangle',
        'background-color': cssVar('--ov-surface'),
        'background-opacity': 0.4,
        'border-color': cssVar('--ov-border'),
        'border-width': 1,
        'border-style': 'dashed',
        'label': 'data(label)',
        'color': cssVar('--ov-text-2'),
        'font-size': 10,
        'text-valign': 'top',
        'text-halign': 'center',
        'padding': 8,
      },
    },
    {
      selector: 'edge',
      style: {
        'curve-style': 'haystack',
        'width': 0.6,
        'line-color': cssVar('--ov-text-2'),
        'opacity': 0.15,
      },
    },
    {
      selector: 'edge.topic-related',
      style: { 'line-style': 'dashed', 'opacity': 0.15, 'width': 0.6 },
    },
    {
      selector: 'edge.shared-tags',
      style: {
        'line-style': 'solid',
        'opacity': 0.30,
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
        'target-arrow-color': cssVar('--ov-text-2'),
        'line-color': cssVar('--ov-text-2'),
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
  let html = `<strong>${escapeHtml(d.label)}</strong>`;
  if (d.type === 'publication') {
    html += `<br><span style="color:var(--ov-text-2);">${escapeHtml(d.authors || '')}</span>`;
    html += `<br><em>${escapeHtml(d.venue || '')}</em> · ${d.year ?? ''}`;
  } else if (d.type === 'software') {
    html += `<br><span style="color:var(--ov-text-2);">${escapeHtml(d.description || '')}</span>`;
  } else if (d.type === 'course') {
    html += `<br><span style="color:var(--ov-text-2);">${escapeHtml(d.description || '')}</span>`;
  } else if (d.type === 'compound') {
    html += `<br><span style="color:var(--ov-text-2);">tutorial group · zoom in to expand</span>`;
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

function applyZoomBehaviour(cy) {
  const update = () => {
    const z = cy.zoom();
    const expanded = z >= ZOOM_THRESHOLD;
    cy.batch(() => {
      cy.nodes('.course').style('display', expanded ? 'element' : 'none');
      cy.nodes('.compound').style('display', expanded ? 'none' : 'element');
    });
  };
  cy.on('zoom', update);
  update();
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
  // tutorial topics share the same palette by ordinal — map their position+1.
  graph.topics.tutorial.forEach((t, i) => m.set(t.slug, ((i % 8) + 1)));
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

  document.getElementById('ov-stat-pub').textContent    = graph.stats.publications;
  document.getElementById('ov-stat-sw').textContent     = graph.stats.software;
  document.getElementById('ov-stat-course').textContent = graph.stats.courses;
  const edgesEl = document.getElementById('ov-stat-edges');
  if (edgesEl) edgesEl.textContent =
    `${graph.stats.edges_total} edges · ${(graph.stats.coverage * 100).toFixed(0)}% coverage`;

  // Mobile: skip Cytoscape entirely; list + search + filters still work.
  if (isMobile) {
    if (loading) loading.textContent = 'graph hidden on small screens';
    initSearch({ graph });
    initList({ graph, cy: stubCy() });
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
          quality: 'default',
          randomize: false,
          animate: false,
          nodeRepulsion: 4500,
          idealEdgeLength: 60,
          edgeElasticity: 0.45,
          gravity: 0.25,
          gravityRange: 3.8,
          numIter: 2500,
          tile: true,
          packComponents: true,
          padding: 30,
        },
  });

  cy.ready(() => {
    loading.style.display = 'none';
    applyZoomBehaviour(cy);
    if (!useCached) persistLayout(cy);
    initSearch({ graph });
    initList({ graph, cy });
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
