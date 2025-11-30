import React, { useState, useEffect } from 'react';
import { Table, Tag, Button, Space, Modal, message, Popconfirm } from 'antd';
import { 
  PlayCircleOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  StopOutlined,
  SyncOutlined,
  LoadingOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { getTrainingJobs, deleteTrainingJob } from '../api/trainingJobs';
import TrainingProgressModal from './TrainingProgressModal';

const TrainingHistory = ({ botId, refreshTrigger }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [progressModalVisible, setProgressModalVisible] = useState(false);

  // Fetch training jobs
  const fetchJobs = async () => {
    if (!botId) return;
    
    setLoading(true);
    try {
      const data = await getTrainingJobs(botId, 20);
      setJobs(data);
    } catch (error) {
      console.error('Failed to fetch training jobs:', error);
      message.error('Failed to load training history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [botId, refreshTrigger]);

  // View job details
  const handleViewDetails = (jobId) => {
    setSelectedJobId(jobId);
    setProgressModalVisible(true);
  };

  // Delete training job
  const handleDelete = async (jobId) => {
    try {
      await deleteTrainingJob(jobId);
      message.success('Training job deleted successfully');
      fetchJobs();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to delete training job');
    }
  };

  // Get status tag
  const getStatusTag = (status) => {
    const statusConfig = {
      pending: { color: 'default', icon: <SyncOutlined spin />, text: 'Pending' },
      running: { color: 'processing', icon: <LoadingOutlined />, text: 'Running' },
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

  // Format duration
  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const columns = [
    {
      title: 'Job ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      render: (id) => <span style={{ fontWeight: 500 }}>#{id}</span>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => getStatusTag(status)
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 100,
      render: (progress, record) => (
        <div>
          {record.status === 'running' ? (
            <Tag color="processing">{progress}%</Tag>
          ) : record.status === 'completed' ? (
            <Tag color="success">100%</Tag>
          ) : (
            <span style={{ color: '#8c8c8c' }}>{progress}%</span>
          )}
        </div>
      )
    },
    {
      title: 'Started',
      dataIndex: 'started_at',
      key: 'started_at',
      width: 150,
      render: (date) => date ? new Date(date).toLocaleString() : '-'
    },
    {
      title: 'Duration',
      dataIndex: 'duration_seconds',
      key: 'duration_seconds',
      width: 100,
      render: (duration) => formatDuration(duration)
    },
    {
      title: 'Action',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record.id)}
          >
            View
          </Button>
          {['completed', 'failed', 'cancelled'].includes(record.status) && (
            <Popconfirm
              title="Delete this training job?"
              description="This will permanently delete the job and all its logs."
              onConfirm={() => handleDelete(record.id)}
              okText="Delete"
              cancelText="Cancel"
              okButtonProps={{ danger: true }}
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                Delete
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <>
      <Table
        columns={columns}
        dataSource={jobs}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showSizeChanger: false,
          showTotal: (total) => `Total ${total} jobs`
        }}
        size="small"
        scroll={{ x: 900 }}
      />

      <TrainingProgressModal
        visible={progressModalVisible}
        jobId={selectedJobId}
        onClose={() => {
          setProgressModalVisible(false);
          setSelectedJobId(null);
          // Refresh list when modal closes
          fetchJobs();
        }}
        onComplete={() => {
          // Refresh list when training completes
          fetchJobs();
        }}
      />
    </>
  );
};

export default TrainingHistory;
