/**
 * main.js — shared utilities loaded on every page.
 * Handles navbar auth state and token refresh on 401.
 */

const API_BASE = '/api';

// ── Navbar: show/hide links based on auth state ─────────────
(function updateNavbar() {
  const token = localStorage.getItem('access_token');
  const logoutBtn = document.getElementById('logoutBtn');
  const loginLink = document.getElementById('loginLink');

  if (token) {
    if (logoutBtn) logoutBtn.style.display = 'inline';
    if (loginLink) loginLink.style.display = 'none';
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', e => {
      e.preventDefault();
      fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      }).finally(() => {
        localStorage.clear();
        window.location.href = '/login';
      });
    });
  }
})();

/**
 * Wrapper around fetch that automatically refreshes the access token
 * once on a 401 response and retries the original request.
 *
 * @param {string} url
 * @param {RequestInit} options
 * @returns {Promise<Response>}
 */
async function authFetch(url, options = {}) {
  const token = localStorage.getItem('access_token');
  options.headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
    Authorization: `Bearer ${token}`,
  };

  let response = await fetch(url, options);

  if (response.status === 401) {
    // Attempt token refresh
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      window.location.href = '/login';
      return response;
    }

    const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${refreshToken}` },
    });

    if (refreshRes.ok) {
      const data = await refreshRes.json();
      localStorage.setItem('access_token', data.data.access_token);
      // Retry original request with new token
      options.headers['Authorization'] = `Bearer ${data.data.access_token}`;
      response = await fetch(url, options);
    } else {
      localStorage.clear();
      window.location.href = '/login';
    }
  }

  return response;
}
