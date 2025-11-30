import React, { useState, useEffect, useRef } from 'react';
import { Modal, Progress, Button, Space, Spin, Tag, Timeline, Empty } from 'antd';
import { 
  PlayCircleOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  LoadingOutlined,
  StopOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { getTrainingJob, getTrainingLogs, cancelTrainingJob } from '../api/trainingJobs';

const TrainingProgressModal = ({ visible, jobId, onClose, onComplete }) => {
  const [job, setJob] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const logsEndRef = useRef(null);
  const pollIntervalRef = useRef(null);

  // Auto-scroll to bottom when new logs arrive
  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Fetch job details and logs
  const fetchJobData = async () => {
    if (!jobId) return;
    
    try {
      const [jobData, logsData] = await Promise.all([
        getTrainingJob(jobId),
        getTrainingLogs(jobId, { limit: 1000 })
      ]);
      
      setJob(jobData);
      setLogs(logsData);
      
      // Auto-scroll to bottom
      setTimeout(scrollToBottom, 100);
      
      // Stop polling if job is completed/failed/cancelled
      if (['completed', 'failed', 'cancelled'].includes(jobData.status)) {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        
        // Notify parent if completed
        if (jobData.status === 'completed' && onComplete) {
          onComplete(jobData);
        }
      }
    } catch (error) {
      console.error('Failed to fetch training data:', error);
    }
  };

  // Start polling when modal opens
  useEffect(() => {
    if (visible && jobId) {
      setLoading(true);
      fetchJobData().finally(() => setLoading(false));
      
      // Poll every 2 seconds
      pollIntervalRef.current = setInterval(fetchJobData, 2000);
    }
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [visible, jobId]);

  // Handle cancel training
  const handleCancel = async () => {
    setCancelling(true);
    try {
      await cancelTrainingJob(jobId);
      await fetchJobData(); // Refresh data
    } catch (error) {
      console.error('Failed to cancel training:', error);
    } finally {
      setCancelling(false);
    }
  };

  // Get status tag
  const getStatusTag = (status) => {
    const statusConfig = {
      pending: { color: 'default', icon: <SyncOutlined spin />, text: 'Pending' },
      running: { color: 'processing', icon: <LoadingOutlined />, text: 'Training' },
      completed: { color: 'success', icon: <CheckCircleOutlined />, text: 'Completed' },
      failed: { color: 'error', icon: <CloseCircleOutlined />, text: 'Failed' },
      cancelled: { color: 'warning', icon: <StopOutlined />, text: 'Cancelled' }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    
    return (
      <Tag icon={config.icon} color={config.color}>
        {config.text}
      </Tag>
    );
  };

  // Get log level color
  const getLogLevelColor = (level) => {
    const colors = {
      DEBUG: '#8c8c8c',
      INFO: '#1890ff',
      WARNING: '#faad14',
      ERROR: '#ff4d4f'
    };
    return colors[level] || colors.INFO;
  };

  // Get progress status
  const getProgressStatus = (status) => {
    if (status === 'completed') return 'success';
    if (status === 'failed' || status === 'cancelled') return 'exception';
    return 'active';
  };

  return (
    <Modal
      title={
        <Space>
          <PlayCircleOutlined style={{ fontSize: 20, color: '#1890ff' }} />
          <span>Training Progress</span>
          {job && getStatusTag(job.status)}
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={800}
      footer={
        <Space>
          {job && ['pending', 'running'].includes(job.status) && (
            <Button 
              danger 
              icon={<StopOutlined />}
              onClick={handleCancel}
              loading={cancelling}
            >
              Cancel Training
            </Button>
          )}
          <Button onClick={onClose}>
            {job && job.status === 'completed' ? 'Done' : 'Close'}
          </Button>
        </Space>
      }
    >
      <Spin spinning={loading}>
        {job ? (
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            {/* Progress Bar */}
            <div>
              <div style={{ marginBottom: 8 }}>
                <span style={{ fontWeight: 500 }}>Progress: {job.progress}%</span>
              </div>
              <Progress 
                percent={job.progress} 
                status={getProgressStatus(job.status)}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
            </div>

            {/* Training Info */}
            <div style={{ 
              background: '#f5f5f5', 
              padding: 12, 
              borderRadius: 8,
              fontSize: 13
            }}>
              <Space direction="vertical" size={4} style={{ width: '100%' }}>
                <div>
                  <span style={{ color: '#8c8c8c' }}>Bot ID:</span>{' '}
                  <span style={{ fontWeight: 500 }}>#{job.bot_id}</span>
                </div>
                {job.started_at && (
                  <div>
                    <span style={{ color: '#8c8c8c' }}>Started:</span>{' '}
                    <span>{new Date(job.started_at).toLocaleString()}</span>
                  </div>
                )}
                {job.completed_at && (
                  <div>
                    <span style={{ color: '#8c8c8c' }}>Completed:</span>{' '}
                    <span>{new Date(job.completed_at).toLocaleString()}</span>
                  </div>
                )}
                {job.duration_seconds && (
                  <div>
                    <span style={{ color: '#8c8c8c' }}>Duration:</span>{' '}
                    <span>{Math.floor(job.duration_seconds / 60)}m {job.duration_seconds % 60}s</span>
                  </div>
                )}
              </Space>
            </div>

            {/* Error Message */}
            {job.error_message && (
              <div style={{ 
                background: '#fff2f0', 
                border: '1px solid #ffccc7',
                padding: 12, 
                borderRadius: 8,
                color: '#ff4d4f'
              }}>
                <div style={{ fontWeight: 500, marginBottom: 4 }}>❌ Error:</div>
                <div style={{ fontSize: 13 }}>{job.error_message}</div>
              </div>
            )}

            {/* Logs */}
            <div>
              <div style={{ 
                fontWeight: 500, 
                marginBottom: 8,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>Training Logs</span>
                <Tag>{logs.length} entries</Tag>
              </div>
              
              <div style={{ 
                background: '#000',
                color: '#0f0',
                fontFamily: 'Monaco, Menlo, "Courier New", monospace',
                fontSize: 12,
                padding: 12,
                borderRadius: 8,
                maxHeight: 300,
                overflowY: 'auto',
                lineHeight: 1.6
              }}>
                {logs.length > 0 ? (
                  <>
                    {logs.map((log, index) => (
                      <div 
                        key={log.id || index}
                        style={{ 
                          marginBottom: 4,
                          color: getLogLevelColor(log.log_level)
                        }}
                      >
                        <span style={{ color: '#666', marginRight: 8 }}>
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                        <span style={{ 
                          color: getLogLevelColor(log.log_level),
                          fontWeight: log.log_level === 'ERROR' ? 'bold' : 'normal'
                        }}>
                          [{log.log_level}]
                        </span>
                        <span style={{ marginLeft: 8 }}>
                          {log.message}
                        </span>
                      </div>
                    ))}
                    <div ref={logsEndRef} />
                  </>
                ) : (
                  <div style={{ color: '#666', textAlign: 'center', padding: 20 }}>
                    No logs yet...
                  </div>
                )}
              </div>
            </div>
          </Space>
        ) : (
          <Empty description="No training data available" />
        )}
      </Spin>
    </Modal>
  );
};

export default TrainingProgressModal;
