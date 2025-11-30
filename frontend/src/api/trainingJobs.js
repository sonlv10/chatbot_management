import axios from './axios';

/**
 * Start a new training job for a bot
 */
export const startTraining = async (botId) => {
  const response = await axios.post(`/api/bots/${botId}/train`);
  return response.data;
};

/**
 * Get training job history for a bot
 */
export const getTrainingJobs = async (botId, limit = 10) => {
  const response = await axios.get(`/api/bots/${botId}/training-jobs`, {
    params: { limit }
  });
  return response.data;
};

/**
 * Get detailed information about a specific training job with logs
 */
export const getTrainingJob = async (jobId) => {
  const response = await axios.get(`/api/training-jobs/${jobId}`);
  return response.data;
};

/**
 * Get logs for a specific training job
 */
export const getTrainingLogs = async (jobId, params = {}) => {
  const response = await axios.get(`/api/training-jobs/${jobId}/logs`, {
    params: {
      limit: params.limit || 100,
      offset: params.offset || 0,
      log_level: params.log_level
    }
  });
  return response.data;
};

/**
 * Cancel a running training job
 */
export const cancelTrainingJob = async (jobId) => {
  const response = await axios.delete(`/api/training-jobs/${jobId}/cancel`);
  return response.data;
};

/**
 * Delete a completed/failed training job and all its logs
 */
export const deleteTrainingJob = async (jobId) => {
  const response = await axios.delete(`/api/training-jobs/${jobId}/delete`);
  return response.data;
};
