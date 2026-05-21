/* Library Management System — Custom JS
 * HTMX and Alpine.js are loaded from CDN in base.html.
 * This file adds only small custom utilities. */

// Auto-dismiss flash messages after 5 seconds (handled by Alpine x-init in template)

// HTMX: after HTMX swap, re-run Alpine on new content
document.addEventListener('htmx:afterSwap', (evt) => {
  if (typeof Alpine !== 'undefined') {
    Alpine.initTree(evt.target);
  }
});

// Confirm delete forms (alternative to onsubmit inline handler)
document.addEventListener('submit', (e) => {
  const form = e.target;
  const msg = form.dataset.confirm;
  if (msg && !window.confirm(msg)) {
    e.preventDefault();
  }
});
