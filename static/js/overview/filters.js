// Overview network — filter rail, URL state, live counts (Phase 4).
// Phase 5 piggybacks on the same `ov-state-change` event with a `matched` payload.

const URL_KEYS = {
  type: 'type', rtopic: 'rtopic',
  method: 'method', from: 'from', to: 'to',
  venue: 'venue', language: 'language',
};

const ALL_TYPES = ['publication', 'software'];

export function initFilters({ graph, cy, store }) {
  const rail = document.getElementById('ov-rail-body');
  rail.innerHTML = '';

  // -------------------- state --------------------------------------------
  const yearsAll = graph.nodes
    .filter(n => n.type === 'publication' && n.year)
    .map(n => n.year);
  const yearMin = Math.min(...yearsAll);
  const yearMax = Math.max(...yearsAll);

  const venues = Array.from(new Set(
    graph.nodes.filter(n => n.type === 'publication' && n.venue).map(n => n.venue)
  )).sort();
  const languages = Array.from(new Set(
    graph.nodes.filter(n => n.type === 'software' && n.language).map(n => n.language)
  )).sort();

  const state = {
    types: new Set(ALL_TYPES),
    rtopics: new Set(),
    methods: new Set(),
    venues: new Set(),
    languages: new Set(),
    yearFrom: yearMin,
    yearTo: yearMax,
  };
  hydrateFromURL(state, { yearMin, yearMax });

  // -------------------- DOM ----------------------------------------------
  const sectionType    = makeChipSection('Type', renderTypeChips(state, graph));
  const sectionRtopic  = makeChipSection('Research topic', renderRTopicChips(state, graph));
  const sectionMethod  = makeChipSection('Method', renderMethodChips(state, graph));
  const sectionYear    = makeYearSlider(state, yearMin, yearMax);
  const sectionVenue   = makeChipSection('Venue', renderVenueChips(state, venues));
  const sectionLang    = makeChipSection('Language', renderLanguageChips(state, languages));
  const reset = document.createElement('button');
  reset.type = 'button';
  reset.className = 'reset';
  reset.textContent = 'Reset all';
  reset.addEventListener('click', () => {
    state.types = new Set(ALL_TYPES);
    state.rtopics.clear(); state.methods.clear();
    state.venues.clear(); state.languages.clear();
    state.yearFrom = yearMin; state.yearTo = yearMax;
    rerenderAll();
  });

  rail.append(sectionType, sectionRtopic, sectionMethod,
              sectionYear, sectionVenue, sectionLang, reset);

  // -------------------- apply --------------------------------------------
  function rerenderAll() {
    sectionType.body.replaceChildren(...renderTypeChips(state, graph));
    sectionRtopic.body.replaceChildren(...renderRTopicChips(state, graph));
    sectionMethod.body.replaceChildren(...renderMethodChips(state, graph));
    sectionVenue.body.replaceChildren(...renderVenueChips(state, venues));
    sectionLang.body.replaceChildren(...renderLanguageChips(state, languages));
    apply();
  }

  function apply() {
    const searchHits = window.__ovSearchHits; // Set<id> | null, owned by search.js
    let matched = computeMatched(graph, state);
    if (searchHits) {
      const intersect = new Set();
      matched.forEach(id => { if (searchHits.has(id)) intersect.add(id); });
      matched = intersect;
    }
    cy.batch(() => {
      cy.nodes().forEach(n => {
        const ok = matched.has(n.id());
        n.style('display', ok ? 'element' : 'none');
        n.style('opacity', ok ? 1 : 0.15);
      });
      cy.edges().forEach(e => {
        const ok = matched.has(e.source().id()) && matched.has(e.target().id());
        e.style('display', ok ? 'element' : 'none');
      });
    });
    updateCounts(matched, graph);
    writeURL(state, { yearMin, yearMax });
    document.dispatchEvent(new CustomEvent('ov-matched', { detail: { matched } }));
  }

  document.addEventListener('ov-state-change', () => rerenderAll());
  document.addEventListener('ov-search-change', () => apply());
  apply();
}

// ============================================================================
// Section builders
// ============================================================================
function makeChipSection(label, chips) {
  const wrap = document.createElement('div');
  const h = document.createElement('h4');
  h.textContent = label;
  const body = document.createElement('div');
  body.className = 'ov-chip-group';
  body.append(...chips);
  wrap.append(h, body);
  wrap.body = body;
  return wrap;
}

function chip({ label, count, pressed, colourIdx, on }) {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = 'ov-chip' + (colourIdx ? ` ov-topic-${colourIdx}` : '');
  b.setAttribute('aria-pressed', pressed ? 'true' : 'false');
  if (colourIdx) {
    const sw = document.createElement('span'); sw.className = 'swatch';
    b.append(sw);
  }
  b.append(document.createTextNode(`${label} · ${count}`));
  b.addEventListener('click', on);
  return b;
}

function renderTypeChips(state, graph) {
  const counts = countsByType(graph);
  return ALL_TYPES.map(t => chip({
    label: capitalise(t), count: counts[t] || 0,
    pressed: state.types.has(t),
    on: () => { toggle(state.types, t); fire(); },
  }));
}

function renderRTopicChips(state, graph) {
  const counts = {};
  graph.nodes.forEach(n => {
    if (n.type !== 'publication' && n.type !== 'software') return;
    (n.topics || []).forEach(t => { counts[t] = (counts[t] || 0) + 1; });
  });
  return graph.topics.research.map(t => chip({
    label: t.label, count: counts[t.slug] || 0,
    pressed: state.rtopics.size === 0 ? false : state.rtopics.has(t.slug),
    colourIdx: t.colour_index,
    on: () => { toggle(state.rtopics, t.slug); fire(); },
  }));
}

function renderMethodChips(state, graph) {
  const counts = {};
  graph.nodes.forEach(n => (n.methods || []).forEach(m => {
    counts[m] = (counts[m] || 0) + 1;
  }));
  return graph.methods.map(m => chip({
    label: m.label, count: counts[m.slug] || 0,
    pressed: state.methods.has(m.slug),
    on: () => { toggle(state.methods, m.slug); fire(); },
  }));
}

function renderVenueChips(state, venues) {
  return venues.slice(0, 12).map(v => chip({
    label: v.length > 28 ? v.slice(0, 27) + '…' : v, count: 0,
    pressed: state.venues.has(v),
    on: () => { toggle(state.venues, v); fire(); },
  }));
}

function renderLanguageChips(state, languages) {
  return languages.map(l => chip({
    label: l, count: 0,
    pressed: state.languages.has(l),
    on: () => { toggle(state.languages, l); fire(); },
  }));
}

function makeYearSlider(state, lo, hi) {
  const wrap = document.createElement('div');
  const h = document.createElement('h4'); h.textContent = 'Year';
  const row = document.createElement('div');
  row.style.cssText = 'display:flex; gap:.4rem; align-items:center; font-family:var(--ov-mono); font-size:.8rem;';
  const a = document.createElement('input');
  a.type = 'range'; a.min = lo; a.max = hi; a.value = state.yearFrom; a.style.flex = '1';
  const b = document.createElement('input');
  b.type = 'range'; b.min = lo; b.max = hi; b.value = state.yearTo; b.style.flex = '1';
  const lbl = document.createElement('span');
  const sync = () => {
    let f = +a.value, t = +b.value;
    if (f > t) { [f, t] = [t, f]; }
    state.yearFrom = f; state.yearTo = t;
    lbl.textContent = `${f}–${t}`;
    fire();
  };
  a.addEventListener('input', sync); b.addEventListener('input', sync);
  lbl.textContent = `${state.yearFrom}–${state.yearTo}`;
  row.append(a, b);
  wrap.append(h, row, lbl);
  return wrap;
}

// ============================================================================
// Filter logic
// ============================================================================
function computeMatched(graph, state) {
  const out = new Set();
  for (const n of graph.nodes) {
    if (!state.types.has(n.type)) continue;
    if (n.type === 'publication') {
      if (n.year && (n.year < state.yearFrom || n.year > state.yearTo)) continue;
      if (state.rtopics.size && !(n.topics || []).some(t => state.rtopics.has(t))) continue;
      if (state.methods.size && !(n.methods || []).some(m => state.methods.has(m))) continue;
      if (state.venues.size && !state.venues.has(n.venue)) continue;
    } else if (n.type === 'software') {
      if (state.rtopics.size && !(n.topics || []).some(t => state.rtopics.has(t))) continue;
      if (state.methods.size && !(n.methods || []).some(m => state.methods.has(m))) continue;
      if (state.languages.size && !state.languages.has(n.language)) continue;
    }
    out.add(n.id);
  }
  return out;
}

function countsByType(graph) {
  return graph.nodes.reduce((a, n) => { a[n.type] = (a[n.type] || 0) + 1; return a; }, {});
}

function updateCounts(matched, graph) {
  const c = { publication: 0, software: 0 };
  for (const n of graph.nodes) if (matched.has(n.id)) c[n.type] = (c[n.type] || 0) + 1;
  document.getElementById('ov-stat-pub').textContent = c.publication;
  document.getElementById('ov-stat-sw').textContent  = c.software;
}

// ============================================================================
// URL state
// ============================================================================
function writeURL(state, { yearMin, yearMax }) {
  const u = new URL(location.href);
  const set = (key, value) => {
    if (value && value.length) u.searchParams.set(key, value);
    else u.searchParams.delete(key);
  };
  set(URL_KEYS.type,    state.types.size === ALL_TYPES.length ? '' : Array.from(state.types).join(','));
  set(URL_KEYS.rtopic,  Array.from(state.rtopics).join(','));
  set(URL_KEYS.method,  Array.from(state.methods).join(','));
  set(URL_KEYS.venue,   Array.from(state.venues).join(','));
  set(URL_KEYS.language, Array.from(state.languages).join(','));
  set(URL_KEYS.from,    state.yearFrom !== yearMin ? String(state.yearFrom) : '');
  set(URL_KEYS.to,      state.yearTo   !== yearMax ? String(state.yearTo)   : '');
  history.replaceState(null, '', u.toString());
}

function hydrateFromURL(state, { yearMin, yearMax }) {
  const u = new URL(location.href);
  const get = (k) => u.searchParams.get(k);
  const types = get(URL_KEYS.type);
  if (types) state.types = new Set(types.split(',').filter(t => ALL_TYPES.includes(t)));
  const fillSet = (key, target) => {
    const v = get(key);
    if (v) v.split(',').filter(Boolean).forEach(s => target.add(s));
  };
  fillSet(URL_KEYS.rtopic, state.rtopics);
  fillSet(URL_KEYS.method, state.methods);
  fillSet(URL_KEYS.venue,  state.venues);
  fillSet(URL_KEYS.language, state.languages);
  const f = parseInt(get(URL_KEYS.from), 10);
  const t = parseInt(get(URL_KEYS.to),   10);
  if (!Number.isNaN(f) && f >= yearMin && f <= yearMax) state.yearFrom = f;
  if (!Number.isNaN(t) && t >= yearMin && t <= yearMax) state.yearTo   = t;
}

// ============================================================================
// helpers
// ============================================================================
function toggle(set, v) { set.has(v) ? set.delete(v) : set.add(v); }
function fire() { document.dispatchEvent(new CustomEvent('ov-state-change')); }
function capitalise(s) { return s ? s[0].toUpperCase() + s.slice(1) : s; }
