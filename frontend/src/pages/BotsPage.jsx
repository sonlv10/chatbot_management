import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Popconfirm,
  message,
  Modal,
  Form,
  Input,
  Select,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  RocketOutlined,
  MessageOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { botsAPI } from '../api/bots';
import { startTraining } from '../api/trainingJobs';
import TrainingProgressModal from '../components/TrainingProgressModal';
import TrainingHistory from '../components/TrainingHistory';

const { Title } = Typography;
const { TextArea } = Input;

const BotsPage = () => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingBot, setEditingBot] = useState(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  
  // Training states
  const [trainingJobId, setTrainingJobId] = useState(null);
  const [trainingModalVisible, setTrainingModalVisible] = useState(false);
  const [historyModalVisible, setHistoryModalVisible] = useState(false);
  const [selectedBotForHistory, setSelectedBotForHistory] = useState(null);
  const [refreshHistory, setRefreshHistory] = useState(0);

  useEffect(() => {
    loadBots();
  }, []);

  const loadBots = async () => {
    setLoading(true);
    try {
      const data = await botsAPI.getAllBots();
      setBots(data);
    } catch (error) {
      message.error('Failed to load bots');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingBot(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (bot) => {
    setEditingBot(bot);
    form.setFieldsValue(bot);
    setModalVisible(true);
  };

  const handleDelete = async (botId) => {
    try {
      await botsAPI.deleteBot(botId);
      message.success('Bot deleted successfully');
      loadBots();
    } catch (error) {
      message.error('Failed to delete bot');
    }
  };

  const handleTrain = async (botId) => {
    try {
      const job = await startTraining(botId);
      setTrainingJobId(job.id);
      setTrainingModalVisible(true);
      message.success('Training started!');
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to start training');
    }
  };

  const handleViewHistory = (bot) => {
    setSelectedBotForHistory(bot);
    setHistoryModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      if (editingBot) {
        await botsAPI.updateBot(editingBot.id, values);
        message.success('Bot updated successfully');
      } else {
        await botsAPI.createBot(values);
        message.success('Bot created successfully');
      }
      setModalVisible(false);
      loadBots();
    } catch (error) {
      message.error('Operation failed');
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Language',
      dataIndex: 'language',
      key: 'language',
      width: 100,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const colors = {
          draft: 'default',
          training: 'processing',
          active: 'success',
          error: 'error',
        };
        return <Tag color={colors[status]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 400,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Button
            size="small"
            icon={<RocketOutlined />}
            onClick={() => handleTrain(record.id)}
            disabled={record.status === 'training'}
          >
            Train
          </Button>
          <Button
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => handleViewHistory(record)}
          >
            History
          </Button>
          <Button
            size="small"
            icon={<MessageOutlined />}
            onClick={() => navigate(`/dashboard/chat/${record.id}`)}
            disabled={record.status !== 'active'}
          >
            Chat
          </Button>
          <Popconfirm
            title="Delete this bot?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2}>My Bots</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Create Bot
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={bots}
        rowKey="id"
        loading={loading}
      />

      <Modal
        title={editingBot ? 'Edit Bot' : 'Create Bot'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="Bot Name"
            rules={[{ required: true, message: 'Please input bot name!' }]}
          >
            <Input placeholder="My Awesome Bot" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Bot description..." />
          </Form.Item>

          <Form.Item
            name="language"
            label="Language"
            initialValue="vi"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="vi">Vietnamese</Select.Option>
              <Select.Option value="en">English</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Training Progress Modal */}
      <TrainingProgressModal
        visible={trainingModalVisible}
        jobId={trainingJobId}
        onClose={() => {
          setTrainingModalVisible(false);
          setTrainingJobId(null);
          loadBots(); // Refresh bots list
        }}
        onComplete={(job) => {
          message.success('Training completed successfully!');
          loadBots();
          setRefreshHistory(prev => prev + 1);
        }}
      />

      {/* Training History Modal */}
      <Modal
        title={
          <Space>
            <HistoryOutlined style={{ color: '#1890ff' }} />
            <span>Training History - {selectedBotForHistory?.name}</span>
          </Space>
        }
        open={historyModalVisible}
        onCancel={() => {
          setHistoryModalVisible(false);
          setSelectedBotForHistory(null);
        }}
        footer={null}
        width={1200}
      >
        {selectedBotForHistory && (
          <TrainingHistory 
            botId={selectedBotForHistory.id} 
            refreshTrigger={refreshHistory}
          />
        )}
      </Modal>
    </div>
  );
};

export default BotsPage;
