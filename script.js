/**
 * script.js — Creepy Movie Recommendation
 *
 * Responsibilities:
 *  - Fetch movie data from api.php without page reloads
 *  - Render movie cards dynamically in the grid
 *  - Handle search, genre filters, hero banner
 *  - Open/close the detail modal with trailer + cast
 *  - Show skeleton loaders and toast messages
 */

'use strict';

// ── Config ───────────────────────────────────────────────────────
const API = 'api.php';   // PHP backend (same directory)

// ── DOM refs ─────────────────────────────────────────────────────
const grid          = document.getElementById('movieGrid');
const sectionTitle  = document.getElementById('sectionTitle');
const resultCount   = document.getElementById('resultCount');
const emptyState    = document.getElementById('emptyState');
const searchInput   = document.getElementById('searchInput');
const searchBtn     = document.getElementById('searchBtn');
const heroTitle     = document.getElementById('heroTitle');
const heroOverview  = document.getElementById('heroOverview');
const heroMeta      = document.getElementById('heroMeta');
const heroBg        = document.getElementById('heroBg');
const heroDetailsBtn = document.getElementById('heroDetailsBtn');
const homeBtn       = document.getElementById('homeBtn');
const toast         = document.getElementById('toast');
const modal         = document.getElementById('detailModal');
const modalClose    = document.getElementById('modalClose');
const modalBackdrop = document.getElementById('modalBackdrop');

// ── State ────────────────────────────────────────────────────────
let heroMovieId = null;
let toastTimer  = null;

// ── Utility: build URL ────────────────────────────────────────────
function apiUrl(params) {
  return API + '?' + new URLSearchParams(params).toString();
}

// ── Utility: show toast ───────────────────────────────────────────
function showToast(msg, duration = 3000) {
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Utility: skeleton loaders ─────────────────────────────────────
function showSkeletons(n = 12) {
  grid.innerHTML = Array.from({length: n}, () =>
    '<div class="skeleton" aria-hidden="true"></div>'
  ).join('');
  emptyState.style.display = 'none';
}

// ── Render hero banner ────────────────────────────────────────────
function setHero(movie) {
  if (!movie) return;
  heroMovieId = movie.id;

  if (movie.backdrop) {
    heroBg.style.backgroundImage = `url('${movie.backdrop}')`;
  } else if (movie.poster) {
    heroBg.style.backgroundImage = `url('${movie.poster}')`;
  }

  heroTitle.textContent   = movie.title || '';
  heroOverview.textContent = (movie.overview || '').slice(0, 200) + (movie.overview?.length > 200 ? '…' : '');

  heroMeta.innerHTML = `
    <span class="rating">⭐ ${(movie.rating || 0).toFixed(1)}</span>
    <span>📅 ${movie.release?.slice(0,4) || 'N/A'}</span>
  `;

  heroDetailsBtn.style.display = 'inline-flex';
}

// ── Render one movie card ─────────────────────────────────────────
function renderCard(movie, delay = 0) {
  const div = document.createElement('div');
  div.className = 'movie-card';
  div.setAttribute('role', 'listitem');
  div.style.animationDelay = `${delay}ms`;
  div.dataset.id = movie.id;

  const rating = (movie.rating || 0).toFixed(1);
  const year   = (movie.release || '').slice(0,4) || '—';

  div.innerHTML = `
    ${movie.poster
      ? `<img class="card-poster" src="${movie.poster}" alt="${escapeHtml(movie.title)}" loading="lazy">`
      : `<div class="card-placeholder"><span>🎬</span>${escapeHtml(movie.title)}</div>`
    }
    <button class="card-play-btn" aria-label="View details for ${escapeHtml(movie.title)}">▶</button>
    <div class="card-overlay">
      <p class="card-title">${escapeHtml(movie.title)}</p>
      <div class="card-meta">
        <span class="card-rating">⭐ ${rating}</span>
        <span>${year}</span>
      </div>
    </div>
  `;

  div.addEventListener('click', () => openModal(movie.id));
  return div;
}

// ── Render full grid ──────────────────────────────────────────────
function renderGrid(movies, section = '') {
  grid.innerHTML = '';

  if (section) sectionTitle.textContent = section;

  if (!movies || movies.length === 0) {
    emptyState.style.display = 'block';
    resultCount.textContent  = '';
    return;
  }

  emptyState.style.display = 'none';
  resultCount.textContent  = `${movies.length} movie${movies.length !== 1 ? 's' : ''}`;

  // Set hero to first movie
  setHero(movies[0]);

  // Render cards with stagger
  movies.forEach((movie, i) => {
    grid.appendChild(renderCard(movie, i * 30));
  });
}

// ── Fetch popular / genre ─────────────────────────────────────────
async function loadMovies(action, genre = '') {
  showSkeletons();
  sectionTitle.textContent = '…';

  try {
    const params = { action };
    if (genre) params.genre = genre;

    const res  = await fetch(apiUrl(params));
    const data = await res.json();

    if (data.status !== 'ok') throw new Error(data.message || 'API error');
    renderGrid(data.movies, data.section);

  } catch (err) {
    console.error(err);
    showToast('⚠️ Failed to load movies. Check your API key.');
    grid.innerHTML = '';
    emptyState.style.display = 'block';
  }
}

// ── Search ────────────────────────────────────────────────────────
async function doSearch() {
  const q = searchInput.value.trim();
  if (!q) { showToast('Type something to search!'); return; }

  showSkeletons(8);

  // Deactivate genre pills
  document.querySelectorAll('.genre-pill').forEach(p => p.classList.remove('active'));

  try {
    const res  = await fetch(apiUrl({ action: 'search', query: q }));
    const data = await res.json();

    if (data.status !== 'ok') throw new Error(data.message);

    if (data.total !== undefined) {
      resultCount.textContent = `${data.total} total results, showing ${data.movies.length}`;
    }

    renderGrid(data.movies, data.section);

  } catch (err) {
    console.error(err);
    showToast('⚠️ Search failed. Please try again.');
  }
}

// ── Open detail modal ─────────────────────────────────────────────
async function openModal(id) {
  // Show modal with loading state
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';

  document.getElementById('modalTitle').textContent   = 'Loading…';
  document.getElementById('modalTagline').textContent = '';
  document.getElementById('modalOverview').textContent = '';
  document.getElementById('modalChips').innerHTML     = '';
  document.getElementById('modalPoster').src          = '';
  document.getElementById('trailerSection').style.display = 'none';
  document.getElementById('castSection').style.display   = 'none';
  document.getElementById('watchSection').style.display  = 'none';
  document.getElementById('modalBackdropImg').style.backgroundImage = '';

  try {
    const res  = await fetch(apiUrl({ action: 'details', id }));
    const data = await res.json();

    if (data.status !== 'ok') throw new Error(data.message);

    const { movie, trailer, cast, watch } = data;

    // Backdrop
    if (movie.backdrop) {
      document.getElementById('modalBackdropImg').style.backgroundImage = `url('${movie.backdrop}')`;
    }

    // Poster
    const poster = document.getElementById('modalPoster');
    if (movie.poster) {
      poster.src = movie.poster;
      poster.alt = movie.title;
    } else {
      poster.src = '';
    }

    // Text
    document.getElementById('modalTitle').textContent    = movie.title   || '';
    document.getElementById('modalTagline').textContent  = movie.tagline || '';
    document.getElementById('modalOverview').textContent = movie.overview || '';

    // Chips
    const chips = document.getElementById('modalChips');
    chips.innerHTML = '';
    if (movie.rating)  chips.innerHTML += `<span class="chip rating">⭐ ${(+movie.rating).toFixed(1)}</span>`;
    if (movie.release) chips.innerHTML += `<span class="chip">📅 ${movie.release.slice(0,4)}</span>`;
    if (movie.runtime) chips.innerHTML += `<span class="chip">⏱ ${movie.runtime} min</span>`;
    (movie.genres || []).forEach(g => {
      chips.innerHTML += `<span class="chip genre">${escapeHtml(g)}</span>`;
    });

    // Trailer
    if (trailer) {
      document.getElementById('trailerSection').style.display = 'block';
      document.getElementById('trailerFrame').src = trailer;
    }

    // Cast
    if (cast && cast.length > 0) {
      document.getElementById('castSection').style.display = 'block';
      const castGrid = document.getElementById('castGrid');
      castGrid.innerHTML = cast.map(a => `
        <div class="cast-card">
          ${a.photo
            ? `<img class="cast-photo" src="${a.photo}" alt="${escapeHtml(a.name)}" loading="lazy">`
            : `<div class="cast-photo" style="background:var(--surface);display:flex;align-items:center;justify-content:center;font-size:2rem;">👤</div>`
          }
          <p class="cast-name">${escapeHtml(a.name)}</p>
          <p class="cast-char">${escapeHtml(a.char || '')}</p>
        </div>
      `).join('');
    }

    // Watch providers
    const cats = ['flatrate','rent','buy'];
    const hasProviders = cats.some(c => watch[c]?.length > 0);
    if (hasProviders) {
      document.getElementById('watchSection').style.display = 'block';
      const wp = document.getElementById('watchProviders');
      wp.innerHTML = '';
      cats.forEach(cat => {
        if (!watch[cat]?.length) return;
        const label = document.createElement('p');
        label.style.cssText = 'font-size:.8rem;color:var(--text-muted);margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.06em;';
        label.textContent = cat === 'flatrate' ? 'Stream' : cat === 'rent' ? 'Rent' : 'Buy';
        wp.appendChild(label);
        const row = document.createElement('div');
        row.className = 'watch-providers';
        watch[cat].forEach(p => {
          if (p.logo) {
            const img = document.createElement('img');
            img.src = p.logo; img.alt = p.name;
            img.title = p.name; img.className = 'provider-logo';
            row.appendChild(img);
          }
        });
        wp.appendChild(row);
      });
      if (watch.link) {
        wp.innerHTML += `<a href="${watch.link}" target="_blank" rel="noopener"
          style="display:inline-block;margin-top:.6rem;font-size:.82rem;color:var(--red);text-decoration:underline;">
          View on JustWatch →</a>`;
      }
    }

  } catch (err) {
    console.error(err);
    document.getElementById('modalTitle').textContent = 'Failed to load';
    showToast('⚠️ Could not load movie details.');
  }
}

// ── Close modal ───────────────────────────────────────────────────
function closeModal() {
  modal.style.display = 'none';
  document.body.style.overflow = '';
  // Stop trailer
  document.getElementById('trailerFrame').src = '';
}

// ── Escape HTML ───────────────────────────────────────────────────
function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

// ── Event Listeners ───────────────────────────────────────────────

// Genre pills
document.querySelectorAll('.genre-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.genre-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    searchInput.value = '';

    const genre = pill.dataset.genre;
    if (genre === 'popular') {
      loadMovies('popular');
    } else if (genre === 'nowplaying') {
      loadMovies('nowplaying');
    } else {
      loadMovies('genre', genre);
    }
  });
});

// Search button
searchBtn.addEventListener('click', doSearch);

// Search on Enter key
searchInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') doSearch();
});

// Clear search on Escape
searchInput.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    searchInput.value = '';
    searchInput.blur();
  }
});

// Hero details button
heroDetailsBtn.addEventListener('click', () => {
  if (heroMovieId) openModal(heroMovieId);
});

// Home button reloads popular
homeBtn.addEventListener('click', e => {
  e.preventDefault();
  searchInput.value = '';
  document.querySelectorAll('.genre-pill').forEach(p => p.classList.remove('active'));
  document.querySelector('[data-genre="popular"]').classList.add('active');
  loadMovies('popular');
});

// Close modal on X or backdrop
modalClose.addEventListener('click', closeModal);
modalBackdrop.addEventListener('click', closeModal);

// Close on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && modal.style.display !== 'none') closeModal();
});

// ── Boot ──────────────────────────────────────────────────────────
loadMovies('popular');
