import apiClient from './axios';

export const trainingAPI = {
  // Get training data with optional filters and sorting
  getTrainingData: async (botId, filters = {}) => {
    const params = new URLSearchParams();
    if (filters.user_message) {
      params.append('user_message', filters.user_message);
    }
    if (filters.bot_response) {
      params.append('bot_response', filters.bot_response);
    }
    if (filters.intent) {
      params.append('intent', filters.intent);
    }
    if (filters.sort_by) {
      params.append('sort_by', filters.sort_by);
    }
    if (filters.sort_order) {
      params.append('sort_order', filters.sort_order);
    }
    
    const queryString = params.toString();
    const url = `/api/bots/${botId}/training/${queryString ? `?${queryString}` : ''}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  // Add training data
  addTrainingData: async (botId, data) => {
    const response = await apiClient.post(`/api/bots/${botId}/training/`, data);
    return response.data;
  },

  // Update training data
  updateTrainingData: async (botId, dataId, data) => {
    const response = await apiClient.put(`/api/bots/${botId}/training/${dataId}`, data);
    return response.data;
  },

  // Upload training file
  uploadTrainingFile: async (botId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(
      `/api/bots/${botId}/training/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Parse file to preview data without saving
  parseTrainingFile: async (botId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(
      `/api/bots/${botId}/training/parse`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Delete training data
  deleteTrainingData: async (botId, dataId) => {
    await apiClient.delete(`/api/bots/${botId}/training/${dataId}`);
  },
};
