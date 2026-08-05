/**
 * API base for LIVE chat.
 * - Local Vite: leave empty → requests go to /api (proxied to :8787)
 * - Production split deploy: set VITE_API_BASE=https://your-api.example.com
 * - Same-origin (FastAPI serves dist): leave empty
 */
export function apiUrl(path) {
  const base = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base}${p}`;
}
