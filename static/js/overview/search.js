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
  input.placeholder = 'Search publications, software, courses…';
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
