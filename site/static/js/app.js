/* LOAM — app.js */

/* ── Theme ───────────────────────────────────────────────────────────────── */
function getTheme() {
  return localStorage.getItem('loam_theme') || 'dark';
}

function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('loam_theme', t);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = t === 'dark' ? '☀' : '☽';
}

document.addEventListener('DOMContentLoaded', () => {
  applyTheme(getTheme());

  const btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', () => {
    applyTheme(getTheme() === 'dark' ? 'light' : 'dark');
  });

  /* ── Reading position ───────────────────────────────────────────────── */
  const dayEl = document.getElementById('current-day');
  if (dayEl) {
    // On a fragment page: save position
    localStorage.setItem('loam_last_read', dayEl.dataset.day);
  } else {
    // On cover page: show continue banner
    const last = localStorage.getItem('loam_last_read');
    if (last) {
      const banner = document.getElementById('continue-banner');
      if (banner) {
        banner.href = banner.dataset.root + 'day/' + last.padStart(3, '0') + '/';
        banner.querySelector('span').textContent = 'Day ' + parseInt(last, 10);
        banner.classList.add('visible');
        setTimeout(() => banner.classList.remove('visible'), 6000);
      }
    }
  }

  /* ── Keyboard navigation (fragment pages) ───────────────────────────── */
  const prevLink = document.getElementById('nav-prev');
  const nextLink = document.getElementById('nav-next');
  if (prevLink || nextLink) {
    document.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowLeft' && prevLink) window.location = prevLink.href;
      if (e.key === 'ArrowRight' && nextLink) window.location = nextLink.href;
    });
  }

  /* ── Codex tabs ─────────────────────────────────────────────────────── */
  document.querySelectorAll('.codex-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.codex-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.codex-section').forEach(s => s.classList.remove('active'));
      tab.classList.add('active');
      const target = document.getElementById(tab.dataset.target);
      if (target) target.classList.add('active');
    });
  });

  /* ── Random fragment ─────────────────────────────────────────────────── */
  const randomLink = document.getElementById('nav-random');
  if (randomLink) {
    const total = parseInt(randomLink.dataset.total, 10);
    const root = randomLink.dataset.root;
    randomLink.addEventListener('click', (e) => {
      e.preventDefault();
      const n = Math.floor(Math.random() * total) + 1;
      window.location = root + 'day/' + String(n).padStart(3, '0') + '/';
    });
  }
});
