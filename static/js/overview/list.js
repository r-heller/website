// Three-column card list with graph↔list sync.

const TYPE_ORDER = ['publication', 'software', 'course'];
const COLUMN_OF = { publication: 'pub', software: 'sw', course: 'course' };

export function initList({ graph, cy }) {
  const cols = {
    pub:    document.getElementById('ov-col-pub'),
    sw:     document.getElementById('ov-col-sw'),
    course: document.getElementById('ov-col-course'),
  };
  if (!cols.pub) return;

  const cardById = new Map();
  const colCounts = { pub: 0, sw: 0, course: 0 };

  // Initial render — every node gets a card; visibility toggled via class.
  for (const t of TYPE_ORDER) {
    const list = cols[COLUMN_OF[t]].querySelector('.ov-col-cards');
    list.replaceChildren();
    const subset = graph.nodes.filter(n => n.type === t);
    sortNodes(subset);
    for (const n of subset) {
      const card = renderCard(n, graph);
      cardById.set(n.id, card);
      list.append(card);
    }
  }

  // Filter sync.
  document.addEventListener('ov-matched', (e) => {
    const matched = e.detail.matched;
    colCounts.pub = colCounts.sw = colCounts.course = 0;
    for (const [id, card] of cardById) {
      const ok = matched.has(id);
      card.style.display = ok ? '' : 'none';
      if (ok) {
        const t = card.dataset.type;
        colCounts[COLUMN_OF[t]]++;
      }
    }
    document.getElementById('ov-col-count-pub').textContent    = colCounts.pub;
    document.getElementById('ov-col-count-sw').textContent     = colCounts.sw;
    document.getElementById('ov-col-count-course').textContent = colCounts.course;
  });

  // Card hover → highlight the matching node in the graph.
  for (const card of cardById.values()) {
    card.addEventListener('mouseenter', () => {
      const n = cy.getElementById(card.dataset.nodeId);
      if (n.nonempty()) n.addClass('hover');
    });
    card.addEventListener('mouseleave', () => {
      const n = cy.getElementById(card.dataset.nodeId);
      if (n.nonempty()) n.removeClass('hover');
    });
  }

  // Node hover → scroll matching card into its column's view + ring it.
  cy.on('mouseover', 'node', (evt) => {
    const id = evt.target.id();
    const card = cardById.get(id);
    if (!card) return;
    card.classList.add('ov-card-hot');
    card.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  });
  cy.on('mouseout', 'node', (evt) => {
    const card = cardById.get(evt.target.id());
    if (card) card.classList.remove('ov-card-hot');
  });
}

// ---------------- helpers --------------------------------------------------

function sortNodes(arr) {
  arr.sort((a, b) => {
    if (a.type === 'publication') {
      if ((b.year || 0) !== (a.year || 0)) return (b.year || 0) - (a.year || 0);
    }
    return a.title.localeCompare(b.title);
  });
}

function renderCard(n, graph) {
  const c = document.createElement('article');
  c.className = 'ov-card';
  c.dataset.nodeId = n.id;
  c.dataset.type = n.type;
  const colourIdx = topicColourIndex(n, graph);
  if (colourIdx) c.classList.add(`ov-topic-${colourIdx}`);

  const glyph = document.createElement('span');
  glyph.className = 'ov-glyph ' +
    (n.type === 'publication' ? 'ov-pub' :
     n.type === 'software'    ? 'ov-sw'  : 'ov-course');

  const title = document.createElement('div');
  title.className = 'ov-card-title';
  title.append(glyph, document.createTextNode(n.title));
  c.append(title);

  const meta = document.createElement('div');
  meta.className = 'ov-card-meta';
  if (n.type === 'publication') {
    const auth = (n.authors || '').split(',').slice(0, 3).join(', ');
    meta.textContent = `${auth || ''} · ${n.year ?? ''} · ${n.venue || ''}`.trim();
  } else if (n.type === 'software') {
    meta.textContent = `${n.language || 'R'} · ${(n.topics || [])[0] || ''}`;
  } else {
    meta.textContent = `CTTIR · ${n.tutorial_topic || ''}`;
  }
  c.append(meta);

  const tags = document.createElement('div');
  tags.className = 'ov-card-tags';
  const tagList = collectTags(n);
  for (const t of tagList.slice(0, 4)) {
    const sp = document.createElement('span');
    sp.className = 'ov-tag';
    sp.textContent = t;
    tags.append(sp);
  }
  c.append(tags);

  if (n.url) {
    const a = document.createElement('a');
    a.className = 'ov-card-link';
    a.href = n.url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent =
      n.type === 'publication' ? 'DOI ↗' :
      n.type === 'software'    ? 'GitHub ↗' :
                                 'CTTIR ↗';
    c.append(a);
  }
  return c;
}

function topicColourIndex(n, graph) {
  if (n.type === 'course') {
    const i = graph.topics.tutorial.findIndex(t => t.slug === n.tutorial_topic);
    return i < 0 ? null : ((i % 8) + 1);
  }
  const slug = n.primary_topic;
  if (!slug) return null;
  const t = graph.topics.research.find(x => x.slug === slug);
  return t ? t.colour_index : null;
}

function collectTags(n) {
  const out = [];
  if (n.topics) out.push(...n.topics);
  if (n.tutorial_topic) out.push(n.tutorial_topic);
  if (n.methods) out.push(...n.methods);
  if (n.tags) out.push(...n.tags);
  return out;
}
