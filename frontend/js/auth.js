/**
 * SConnect Auth - foundation for auth state/flows
 * Server-side session is source of truth. HttpOnly session cookie.
 * No JWT, no localStorage auth, no URL user_id, no fake login behavior.
 */

import { api, ApiError } from './api.js';

/**
 * Check authentication status and optionally required role
 * @param {string} [requiredRole] - Optional role required (e.g., 'admin', 'coach', 'player')
 * @returns {Promise<{ authenticated: boolean, user?: object, role?: string }>}
 */
export async function checkAuth(requiredRole = null) {
  try {
    const response = await api.get('/auth/me');
    const payload = response.data || {};
    const user = payload.user || payload;

    if (!user) {
      return { authenticated: false };
    }

    const userRole = user.role || user.user_role || user.userType;

    if (requiredRole && userRole !== requiredRole) {
      return { authenticated: true, user, role: userRole, authorized: false };
    }

    return {
      authenticated: true,
      user,
      role: userRole,
      authorized: requiredRole ? true : true,
    };
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      return { authenticated: false };
    }
    return { authenticated: false };
  }
}

/**
 * Logout current session
 * @returns {Promise<void>}
 */
export async function logout() {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    // Ignore errors on logout - session may already be cleared
  }
}

/**
 * Redirect to login page
 */
export function redirectToLogin() {
  window.location.href = '/index.html';
}

/**
 * Redirect to dashboard based on role
 * @param {string} [role] - User role
 */
export function redirectToDashboard(role = null) {
  const routes = {
    player: '/player-dashboard.html',
    coach: '/coach-dashboard.html',
    club: '/club-dashboard.html',
    organizer: '/organizer-dashboard.html',
    referee: '/referee-dashboard.html',
    admin: '/admin-portal.html',
  };

  const target = routes[role] || '/index.html';
  window.location.href = target;
}

export default {
  checkAuth,
  logout,
  redirectToLogin,
  redirectToDashboard,
};