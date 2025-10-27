/**
 * API service for backend communication
 */
import axios from 'axios';

// Use dynamic API URL based on current hostname
// This allows access from both localhost and Tailscale URLs
const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // In development, use the same hostname as the frontend with backend port
  const hostname = window.location.hostname;
  return `http://${hostname}:8619`;
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Artist API calls
export const artistAPI = {
  search: async (query, limit = 10) => {
    const response = await api.get('/artists/search', {
      params: { query, limit },
    });
    return response.data;
  },

  follow: async (artistData) => {
    const response = await api.post('/artists/follow', artistData);
    return response.data;
  },

  getFollowed: async () => {
    const response = await api.get('/artists/followed');
    return response.data;
  },

  unfollow: async (artistId) => {
    const response = await api.delete(`/artists/${artistId}`);
    return response.data;
  },

  refresh: async (artistId) => {
    const response = await api.post(`/artists/${artistId}/refresh`);
    return response.data;
  },

  getReleases: async (artistId) => {
    const response = await api.get(`/artists/${artistId}/releases`);
    return response.data;
  },
};

// Release API calls
export const releaseAPI = {
  getAll: async (onlyNew = false, artistId = null) => {
    const params = {};
    if (onlyNew) params.only_new = true;
    if (artistId) params.artist_id = artistId;

    const response = await api.get('/releases/', { params });
    return response.data;
  },

  getLatest: async (limit = null) => {
    const params = {};
    if (limit) params.limit = limit;

    const response = await api.get('/releases/latest', { params });
    return response.data;
  },

  markSeen: async (releaseId) => {
    const response = await api.post(`/releases/${releaseId}/mark-seen`);
    return response.data;
  },

  markAllSeen: async () => {
    const response = await api.post('/releases/mark-all-seen');
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/releases/stats');
    return response.data;
  },

  getTracks: async (releaseId) => {
    const response = await api.get(`/releases/${releaseId}/tracks`);
    return response.data;
  },
};

// Integration API calls (Last.fm, Jellyfin, and Plex)
export const integrationAPI = {
  // Server Status
  checkStatus: async () => {
    const response = await api.get('/integrations/status');
    return response.data;
  },

  // Last.fm
  importLastFm: async (period = 'overall', limit = 50) => {
    const response = await api.post('/integrations/lastfm/import', {
      period,
      limit,
    });
    return response.data;
  },

  // Jellyfin
  checkJellyfin: async (releaseId) => {
    const response = await api.post(`/integrations/jellyfin/check/${releaseId}`);
    return response.data;
  },

  checkAllJellyfin: async () => {
    const response = await api.post('/integrations/jellyfin/check-all');
    return response.data;
  },

  // Plex
  checkPlex: async (releaseId) => {
    const response = await api.post(`/integrations/plex/check/${releaseId}`);
    return response.data;
  },

  checkAllPlex: async () => {
    const response = await api.post('/integrations/plex/check-all');
    return response.data;
  },
};

export default api;
