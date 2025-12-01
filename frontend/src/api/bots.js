import apiClient from './axios';

export const botsAPI = {
  // Get all bots
  getAllBots: async () => {
    const response = await apiClient.get('/api/bots/');
    return response.data;
  },

  // Get bot by ID
  getBot: async (botId) => {
    const response = await apiClient.get(`/api/bots/${botId}`);
    return response.data;
  },

  // Create new bot
  createBot: async (botData) => {
    const response = await apiClient.post('/api/bots/', botData);
    return response.data;
  },

  // Update bot
  updateBot: async (botId, botData) => {
    const response = await apiClient.put(`/api/bots/${botId}`, botData);
    return response.data;
  },

  // Delete bot
  deleteBot: async (botId) => {
    await apiClient.delete(`/api/bots/${botId}`);
  },

  // Train bot
  trainBot: async (botId) => {
    const response = await apiClient.post(`/api/bots/${botId}/train`);
    return response.data;
  },

  // Get training sessions
  getTrainingSessions: async (botId) => {
    const response = await apiClient.get(`/api/bots/${botId}/training/sessions`);
    return response.data;
  },

  // Chat with bot
  chatWithBot: async (botId, message, sessionId = null, isSave = true) => {
    const params = sessionId ? { session_id: sessionId } : {};
    const response = await apiClient.post(
      `/api/bots/${botId}/chat`,
      {
        message,
        sender_id: sessionId || 'user',
        isSave: isSave,
      },
      { params }
    );
    return response.data;
  },

  // Get conversations
  getConversations: async (botId, limit = 50) => {
    const response = await apiClient.get(`/api/bots/${botId}/conversations`, {
      params: { limit },
    });
    return response.data;
  },
};
