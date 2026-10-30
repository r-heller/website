// Lightweight client-side search over graph.json node text fields.
// Runs in <1 ms for our 631-node corpus; debounced at 100 ms for keystrokes.

const DEBOUNCE_MS = 100;

export function initSearch({ graph }) {
  const input = document.getElementById('ov-search');
  if (!input) return;

  // Pre-build a flat haystack per node so each keystroke is just substring scans.
  const haystacks = new Map();
  for (const n of graph.nodes) {
    const parts = [n.title, n.venue, n.authors, n.description, n.language];
    if (n.tags) parts.push(n.tags.join(' '));
    haystacks.set(n.id, (parts.filter(Boolean).join(' ')).toLowerCase());
  }

  input.disabled = false;
  input.placeholder = 'Search publications and software…';
  input.setAttribute('aria-label', 'Search');

  let timer = null;
  const onChange = () => {
    clearTimeout(timer);
    timer = setTimeout(() => apply(input.value), DEBOUNCE_MS);
  };
  input.addEventListener('input', onChange);

  // `/` to focus, `Esc` to clear.
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
      input.select();
    } else if (e.key === 'Escape' && document.activeElement === input) {
      input.value = '';
      apply('');
      input.blur();
    }
  });

  function apply(raw) {
    const q = raw.trim().toLowerCase();
    if (!q) {
      window.__ovSearchHits = null;
    } else {
      const tokens = q.split(/\s+/).filter(Boolean);
      const hits = new Set();
      for (const [id, hay] of haystacks) {
        if (tokens.every(t => hay.includes(t))) hits.add(id);
      }
      window.__ovSearchHits = hits;
    }
    document.dispatchEvent(new CustomEvent('ov-search-change'));
  }
}

// The list is usable with a keyboard and when the graph library is unavailable.
export function initList({ graph }) {
  const list = document.getElementById('ov-results');
  const status = document.getElementById('ov-results-status');
  if (!list || !status) return;
  function render(matched) {
    const nodes = graph.nodes.filter(n => matched.has(n.id));
    const fragment = document.createDocumentFragment();
    for (const n of nodes) {
      const item = document.createElement('li');
      const title = document.createElement('a');
      title.textContent = n.title;
      try {
        const url = new URL(n.url);
        if (['http:', 'https:'].includes(url.protocol)) title.href = url.href;
      } catch { /* An unavailable destination remains readable text. */ }
      item.append(title);
      const details = [n.type === 'publication' ? 'Publication' : 'Software',
                       n.year, n.venue || n.description].filter(Boolean).join(' · ');
      const description = document.createElement('p');
      description.textContent = details;
      item.append(description);
      fragment.append(item);
    }
    list.replaceChildren(fragment);
    status.textContent = nodes.length ? `${nodes.length} matching items` : 'No matching items. Clear the search or reset the filters.';
  }
  document.addEventListener('ov-matched', e => render(e.detail.matched));
  render(new Set(graph.nodes.map(n => n.id)));
}
