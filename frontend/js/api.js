// Central API Client for Mother Theresa Transport
const API_BASE = '/api';

const API = {
  getToken() {
    return localStorage.getItem('mtt_token');
  },

  setToken(token, ownerName, username) {
    localStorage.setItem('mtt_token', token);
    if (ownerName) localStorage.setItem('mtt_owner_name', ownerName);
    if (username) localStorage.setItem('mtt_username', username);
  },

  clearAuth() {
    localStorage.removeItem('mtt_token');
    localStorage.removeItem('mtt_owner_name');
    localStorage.removeItem('mtt_username');
  },

  getOwnerName() {
    return localStorage.getItem('mtt_owner_name') || 'Owner';
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401) {
        this.clearAuth();
        if (!window.location.pathname.includes('/login') && window.location.pathname !== '/') {
          window.location.href = '/login';
        }
        throw new Error('Session expired. Please log in again.');
      }

      const contentType = response.headers.get('content-type');
      let data = null;
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        const errorMsg = data && data.detail ? data.detail : (typeof data === 'string' ? data : 'An error occurred');
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  put(endpoint, body) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body)
    });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};

// UI Notification Toast Helper
window.showToast = function(message, type = 'info') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `toast-item toast-${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <span>${message}</span>
    </div>
  `;

  toastContainer.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 10);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};
