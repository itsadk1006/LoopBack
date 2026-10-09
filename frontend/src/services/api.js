const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData && errorData.detail) {
        errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : JSON.stringify(errorData.detail);
      }
    } catch {
      // Fallback to HTTP status text
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const api = {
  async getIncidents() {
    const res = await fetch(`${API_BASE_URL}/incidents`);
    return handleResponse(res);
  },

  async getIncident(id) {
    const res = await fetch(`${API_BASE_URL}/incidents/${id}`);
    return handleResponse(res);
  },

  async investigateIncident(id) {
    const res = await fetch(`${API_BASE_URL}/incidents/${id}/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse(res);
  },

  async performAction(id, action, notes = '') {
    const res = await fetch(`${API_BASE_URL}/incidents/${id}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, notes }),
    });
    return handleResponse(res);
  },
};
