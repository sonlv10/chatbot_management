import { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Upload,
  message,
  Space,
  Popconfirm,
  Select,
  Typography,
  Spin,
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { botsAPI } from '../api/bots';
import { trainingAPI } from '../api/training';

const { Title } = Typography;

const TrainingDataPage = () => {
  const [bots, setBots] = useState([]);
  const [selectedBotId, setSelectedBotId] = useState(null);
  const [trainingData, setTrainingData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBots();
  }, []);

  useEffect(() => {
    if (selectedBotId) {
      loadTrainingData();
    }
  }, [selectedBotId]);

  const loadBots = async () => {
    try {
      const data = await botsAPI.getAllBots();
      setBots(data);
      if (data.length > 0 && !selectedBotId) {
        setSelectedBotId(data[0].id);
      }
    } catch (error) {
      message.error('Failed to load bots');
    }
  };

  const loadTrainingData = async () => {
    setLoading(true);
    try {
      const data = await trainingAPI.getTrainingData(selectedBotId);
      setTrainingData(data);
    } catch (error) {
      message.error('Failed to load training data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    try {
      await trainingAPI.uploadTrainingFile(selectedBotId, file);
      message.success('Training data uploaded successfully');
      loadTrainingData();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Upload failed');
    }
    return false; // Prevent default upload behavior
  };

  const handleDelete = async (dataId) => {
    try {
      await trainingAPI.deleteTrainingData(selectedBotId, dataId);
      message.success('Training data deleted');
      loadTrainingData();
    } catch (error) {
      message.error('Failed to delete training data');
    }
  };

  const handleDownloadTemplate = () => {
    const template = [
      {
        user: 'Xin chào',
        bot: 'Xin chào! Tôi có thể giúp gì cho bạn?',
        intent: 'greeting',
      },
      {
        user: 'Giá bao nhiêu?',
        bot: 'Sản phẩm này giá 299.000đ',
        intent: 'price_inquiry',
      },
    ];

    const blob = new Blob([JSON.stringify(template, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'training_template.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const columns = [
    {
      title: 'User Message',
      dataIndex: 'user_message',
      key: 'user_message',
      width: '35%',
    },
    {
      title: 'Bot Response',
      dataIndex: 'bot_response',
      key: 'bot_response',
      width: '35%',
    },
    {
      title: 'Intent',
      dataIndex: 'intent',
      key: 'intent',
      width: '20%',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: '10%',
      render: (_, record) => (
        <Popconfirm
          title="Delete this training data?"
          onConfirm={() => handleDelete(record.id)}
        >
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2}>Training Data</Title>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={handleDownloadTemplate}>
            Download Template
          </Button>
        </Space>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%' }} direction="vertical">
          <div>
            <strong>Select Bot: </strong>
            <Select
              style={{ width: 300 }}
              value={selectedBotId}
              onChange={setSelectedBotId}
              options={bots.map((bot) => ({
                label: bot.name,
                value: bot.id,
              }))}
            />
          </div>

          {selectedBotId && (
            <Upload beforeUpload={handleUpload} accept=".json,.csv,.txt,.yml,.yaml,.md,.markdown" maxCount={1}>
              <Button icon={<UploadOutlined />} type="primary">
                Upload Training Data
              </Button>
            </Upload>
          )}

          <div style={{ fontSize: 12, color: '#666' }}>
            Supported formats: JSON, CSV, YAML, TXT, Markdown
          </div>
        </Space>
      </Card>

      {selectedBotId && (
        <Card title={`Training Data (${trainingData.length} items)`}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 50 }}>
              <Spin size="large" />
            </div>
          ) : (
            <Table
              columns={columns}
              dataSource={trainingData}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          )}
        </Card>
      )}
    </div>
  );
};

export default TrainingDataPage;
