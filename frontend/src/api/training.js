import apiClient from './axios';

export const trainingAPI = {
  // Get training data
  getTrainingData: async (botId) => {
    const response = await apiClient.get(`/api/bots/${botId}/training/`);
    return response.data;
  },

  // Add training data
  addTrainingData: async (botId, data) => {
    const response = await apiClient.post(`/api/bots/${botId}/training/`, {
      data,
    });
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

  // Delete training data
  deleteTrainingData: async (botId, dataId) => {
    await apiClient.delete(`/api/bots/${botId}/training/${dataId}`);
  },
};
