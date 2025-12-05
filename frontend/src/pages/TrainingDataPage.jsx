import { useState, useEffect, useMemo } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
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
  Modal,
  Form,
  Input,
  Tooltip,
  Tag,
  Tabs,
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  DownloadOutlined,
  PlusOutlined,
  EditOutlined,
  ExportOutlined,
  SearchOutlined,
  RocketOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { botsAPI } from '../api/bots';
import { trainingAPI } from '../api/training';
import { startTraining } from '../api/trainingJobs';
import TrainingProgressModal from '../components/TrainingProgressModal';
import TrainingHistory from '../components/TrainingHistory';

const { Title } = Typography;
const { TextArea } = Input;

const TrainingDataPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [bots, setBots] = useState([]);
  const [selectedBotId, setSelectedBotId] = useState(() => {
    // Check if bot ID is passed from navigation state
    if (location.state?.botId) {
      return location.state.botId;
    }
    // Otherwise, load from localStorage
    const saved = localStorage.getItem('selectedBotId');
    return saved ? parseInt(saved) : null;
  });
  const [trainingData, setTrainingData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isExportModalVisible, setIsExportModalVisible] = useState(false);
  const [exportMode, setExportMode] = useState('export'); // 'export' or 'template'
  const [isPreviewModalVisible, setIsPreviewModalVisible] = useState(false);
  const [previewData, setPreviewData] = useState([]);
  const [editingPreviewKey, setEditingPreviewKey] = useState(null);
  const [previewMode, setPreviewMode] = useState('upload'); // 'upload' or 'add'
  const [uploadFile, setUploadFile] = useState(null);
  const [fileList, setFileList] = useState([]);
  const [editingRecord, setEditingRecord] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [filteredInfo, setFilteredInfo] = useState({});
  const [sortedInfo, setSortedInfo] = useState({});
  const [currentPage, setCurrentPage] = useState(() => {
    const page = searchParams.get('page');
    return page ? parseInt(page) : 1;
  });
  const [pageSize, setPageSize] = useState(() => {
    const size = searchParams.get('pageSize');
    return size ? parseInt(size) : 10;
  });
  const [serverFilters, setServerFilters] = useState({
    user_message: '',
    bot_response: '',
    intent: '',
    sort_by: 'created_at',
    sort_order: 'desc'
  });
  const [form] = Form.useForm();
  
  // Training states
  const [trainingJobId, setTrainingJobId] = useState(null);
  const [trainingModalVisible, setTrainingModalVisible] = useState(false);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [activeTab, setActiveTab] = useState('data');

  // Get unique intents for filter
  const uniqueIntents = useMemo(() => {
    const intents = [...new Set(trainingData.map(item => item.intent))].filter(Boolean);
    return intents.sort();
  }, [trainingData]);

  useEffect(() => {
    loadBots();
    
    // Reload bots when returning to this page to detect deleted bots
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadBots();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Handle bot selection from navigation state
  useEffect(() => {
    if (location.state?.botId && location.state.botId !== selectedBotId) {
      setSelectedBotId(location.state.botId);
    }
  }, [location.state?.botId]);

  // Sync URL params with pagination state
  useEffect(() => {
    const params = new URLSearchParams();
    if (currentPage > 1) {
      params.set('page', currentPage.toString());
    }
    if (pageSize !== 10) {
      params.set('pageSize', pageSize.toString());
    }
    
    const newSearch = params.toString();
    const currentSearch = window.location.search.slice(1);
    
    if (newSearch !== currentSearch) {
      navigate(`${location.pathname}?${newSearch}`, { replace: true });
    }
  }, [currentPage, pageSize]);

  useEffect(() => {
    if (selectedBotId) {
      loadTrainingData();
      // Save selected bot to localStorage
      localStorage.setItem('selectedBotId', selectedBotId.toString());
    }
  }, [selectedBotId, serverFilters]);

  const loadBots = async () => {
    try {
      const data = await botsAPI.getAllBots();
      setBots(data);
      
      if (data.length === 0) {
        // No bots available, clear selection
        setSelectedBotId(null);
        localStorage.removeItem('selectedBotId');
        setTrainingData([]);
      } else if (!selectedBotId) {
        // Has bots but no selection, select first bot
        setSelectedBotId(data[0].id);
      } else {
        // Check if selected bot still exists
        const botExists = data.some(bot => bot.id === selectedBotId);
        if (!botExists) {
          // Selected bot was deleted, select first available bot
          setSelectedBotId(data[0].id);
        }
      }
    } catch (error) {
      message.error('Failed to load bots');
    }
  };

  const handleTrain = async () => {
    if (!selectedBotId) {
      message.warning('Please select a bot first');
      return;
    }
    
    try {
      const job = await startTraining(selectedBotId);
      setTrainingJobId(job.id);
      setTrainingModalVisible(true);
      message.success('Training started!');
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to start training');
    }
  };

  const loadTrainingData = async () => {
    if (!selectedBotId) {
      setTrainingData([]);
      return;
    }
    
    setLoading(true);
    try {
      const data = await trainingAPI.getTrainingData(selectedBotId, serverFilters);
      setTrainingData(data);
      setSelectedRowKeys([]); // Reset selection when loading new data
    } catch (error) {
      message.error('Failed to load training data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    try {
      setLoading(true);
      const result = await trainingAPI.parseTrainingFile(selectedBotId, file);
      setPreviewData(result.data);
      setUploadFile(file);
      setPreviewMode('upload');
      setIsPreviewModalVisible(true);
    } catch (error) {
      message.error(error.response?.data?.detail || 'Failed to parse file');
    } finally {
      setLoading(false);
    }
    return false; // Prevent default upload behavior
  };

  const handleConfirmUpload = async () => {
    // Validate preview data
    const invalidRows = previewData.filter(
      (item) => !item.user || !item.bot || !item.intent
    );
    
    if (invalidRows.length > 0) {
      message.error('Please fill in all fields for all rows');
      return;
    }

    try {
      setLoading(true);
      
      if (previewMode === 'add') {
        // Batch add multiple items
        for (const item of previewData) {
          await trainingAPI.addTrainingData(selectedBotId, {
            user_message: item.user,
            bot_response: item.bot,
            intent: item.intent,
          });
        }
        message.success(`${previewData.length} items added successfully`);
      } else {
        // Upload from file
        const formData = new FormData();
        const jsonBlob = new Blob([JSON.stringify(previewData)], { type: 'application/json' });
        formData.append('file', jsonBlob, 'edited_data.json');
        
        await trainingAPI.uploadTrainingFile(selectedBotId, jsonBlob);
        message.success(`Training data uploaded successfully (${previewData.length} items)`);
      }
      
      setIsPreviewModalVisible(false);
      setPreviewData([]);
      setUploadFile(null);
      setEditingPreviewKey(null);
      setPreviewMode('upload');
      setFileList([]); // Reset Upload component
      loadTrainingData();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelUpload = () => {
    setIsPreviewModalVisible(false);
    setPreviewData([]);
    setUploadFile(null);
    setEditingPreviewKey(null);
    setPreviewMode('upload');
    setFileList([]); // Reset Upload component
  };

  const handleAddPreviewRow = () => {
    const newRow = {
      user: '',
      bot: '',
      intent: 'unknown',
      isNew: true,
    };
    setPreviewData([...previewData, newRow]);
    setEditingPreviewKey(previewData.length);
  };

  const handleSavePreviewRow = (key, record) => {
    const newData = [...previewData];
    const index = newData.findIndex((item, idx) => idx === key);
    if (index > -1) {
      newData[index] = { ...record, isNew: false };
      setPreviewData(newData);
      setEditingPreviewKey(null);
    }
  };

  const handleDeletePreviewRow = (key) => {
    setPreviewData(previewData.filter((_, idx) => idx !== key));
  };

  const handleEditPreviewRow = (key) => {
    setEditingPreviewKey(key);
  };

  const handleCancelPreviewEdit = () => {
    // Remove row if it was newly added and not saved
    if (editingPreviewKey !== null) {
      const record = previewData[editingPreviewKey];
      if (record?.isNew) {
        setPreviewData(previewData.filter((_, idx) => idx !== editingPreviewKey));
      }
    }
    setEditingPreviewKey(null);
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
    setExportMode('template');
    setIsExportModalVisible(true);
  };

  const handleExport = () => {
    if (trainingData.length === 0) {
      message.warning('No data to export');
      return;
    }
    setExportMode('export');
    setIsExportModalVisible(true);
  };

  const exportToJSON = (data) => {
    const exportData = data.map(({ id, bot_id, created_at, ...rest }) => ({
      user: rest.user_message,
      bot: rest.bot_response,
      intent: rest.intent,
    }));
    return JSON.stringify(exportData, null, 2);
  };

  const exportToCSV = (data) => {
    const headers = 'user,bot,intent\n';
    const rows = data.map(item => {
      const user = `"${item.user_message.replace(/"/g, '""')}"`;
      const bot = `"${item.bot_response.replace(/"/g, '""')}"`;
      const intent = item.intent;
      return `${user},${bot},${intent}`;
    }).join('\n');
    return headers + rows;
  };

  const exportToYAML = (data) => {
    const groupedByIntent = data.reduce((acc, item) => {
      if (!acc[item.intent]) {
        acc[item.intent] = [];
      }
      acc[item.intent].push({
        user: item.user_message,
        bot: item.bot_response,
      });
      return acc;
    }, {});

    let yaml = 'nlu:\n';
    Object.entries(groupedByIntent).forEach(([intent, items]) => {
      yaml += `- intent: ${intent}\n`;
      yaml += '  examples: |\n';
      items.forEach(item => {
        yaml += `    - ${item.user}\n`;
      });
    });
    return yaml;
  };

  const exportToTXT = (data) => {
    return data.map(item => {
      return `User: ${item.user_message}\nBot: ${item.bot_response}\nIntent: ${item.intent}\n---`;
    }).join('\n');
  };

  const getTemplateData = () => [
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
    {
      user: 'Làm thế nào để liên hệ?',
      bot: 'Bạn có thể liên hệ qua email: support@example.com hoặc hotline: 1900-xxxx',
      intent: 'contact_info',
    },
  ];

  const exportTemplateToJSON = () => {
    const template = getTemplateData();
    return JSON.stringify(template, null, 2);
  };

  const exportTemplateToCSV = () => {
    const template = getTemplateData();
    const headers = 'user,bot,intent\n';
    const rows = template.map(item => {
      const user = `"${item.user.replace(/"/g, '""')}"`;
      const bot = `"${item.bot.replace(/"/g, '""')}"`;
      const intent = item.intent;
      return `${user},${bot},${intent}`;
    }).join('\n');
    return headers + rows;
  };

  const exportTemplateToTXT = () => {
    const template = getTemplateData();
    return template.map(item => {
      return `User: ${item.user}\nBot: ${item.bot}\nIntent: ${item.intent}\n---`;
    }).join('\n');
  };

  const exportToMarkdown = (data) => {
    const groupedByIntent = data.reduce((acc, item) => {
      if (!acc[item.intent]) {
        acc[item.intent] = [];
      }
      acc[item.intent].push(item.user_message);
      return acc;
    }, {});

    let markdown = '';
    Object.entries(groupedByIntent).forEach(([intent, messages]) => {
      markdown += `## intent:${intent}\n`;
      messages.forEach(msg => {
        markdown += `- ${msg}\n`;
      });
      markdown += '\n';
    });
    return markdown;
  };

  const handleExportWithFormat = (format) => {
    let content, mimeType, extension;

    if (exportMode === 'template') {
      // Download template
      switch (format) {
        case 'json':
          content = exportTemplateToJSON();
          mimeType = 'application/json';
          extension = 'json';
          break;
        case 'csv':
          content = exportTemplateToCSV();
          mimeType = 'text/csv';
          extension = 'csv';
          break;
        case 'txt':
          content = exportTemplateToTXT();
          mimeType = 'text/plain';
          extension = 'txt';
          break;
        default:
          return;
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `training_template.${extension}`;
      a.click();
      URL.revokeObjectURL(url);
      
      setIsExportModalVisible(false);
      message.success(`Template downloaded as ${format.toUpperCase()} successfully`);
    } else {
      // Export data
      const dataToExport = selectedRowKeys.length > 0
        ? trainingData.filter(item => selectedRowKeys.includes(item.id))
        : trainingData;

      switch (format) {
        case 'json':
          content = exportToJSON(dataToExport);
          mimeType = 'application/json';
          extension = 'json';
          break;
        case 'csv':
          content = exportToCSV(dataToExport);
          mimeType = 'text/csv';
          extension = 'csv';
          break;
        case 'txt':
          content = exportToTXT(dataToExport);
          mimeType = 'text/plain';
          extension = 'txt';
          break;
        default:
          return;
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const prefix = selectedRowKeys.length > 0 ? 'selected' : 'all';
      const count = selectedRowKeys.length > 0 ? selectedRowKeys.length : trainingData.length;
      a.download = `training_data_${prefix}_${count}_items_${new Date().toISOString().split('T')[0]}.${extension}`;
      a.click();
      URL.revokeObjectURL(url);
      
      setIsExportModalVisible(false);
      message.success(`Exported ${count} items as ${format.toUpperCase()} successfully`);
    }
  };

  const showAddModal = () => {
    // Use preview modal for batch adding
    setPreviewData([
      {
        user: '',
        bot: '',
        intent: 'unknown',
        isNew: true,
      }
    ]);
    setPreviewMode('add');
    setEditingPreviewKey(0);
    setIsPreviewModalVisible(true);
  };

  const showEditModal = (record) => {
    setEditingRecord(record);
    form.setFieldsValue({
      user_message: record.user_message,
      bot_response: record.bot_response,
      intent: record.intent,
    });
    setIsModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingRecord) {
        // Update existing record
        await trainingAPI.updateTrainingData(selectedBotId, editingRecord.id, values);
        message.success('Training data updated successfully');
      } else {
        // Add new record
        await trainingAPI.addTrainingData(selectedBotId, values);
        message.success('Training data added successfully');
      }
      
      setIsModalVisible(false);
      form.resetFields();
      loadTrainingData();
    } catch (error) {
      if (error.errorFields) {
        // Validation error
        return;
      }
      message.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
    setEditingRecord(null);
  };

  const handleDeleteSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('Please select items to delete');
      return;
    }

    try {
      // Delete all selected items
      await Promise.all(
        selectedRowKeys.map(id => trainingAPI.deleteTrainingData(selectedBotId, id))
      );
      message.success(`Deleted ${selectedRowKeys.length} items successfully`);
      setSelectedRowKeys([]);
      loadTrainingData();
    } catch (error) {
      message.error('Failed to delete selected items');
    }
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
    selections: [
      Table.SELECTION_ALL,
      Table.SELECTION_INVERT,
      Table.SELECTION_NONE,
    ],
  };

  const handleTableChange = (pagination, filters, sorter) => {
    setFilteredInfo(filters);
    setSortedInfo(sorter);
    
    // Update pagination state
    if (pagination.current) {
      setCurrentPage(pagination.current);
    }
    if (pagination.pageSize) {
      setPageSize(pagination.pageSize);
      // Reset to page 1 if page size changes
      if (pagination.pageSize !== pageSize) {
        setCurrentPage(1);
      }
    }
    
    // Update server filters for intent
    if (filters.intent && filters.intent.length > 0) {
      setServerFilters(prev => ({ ...prev, intent: filters.intent[0] }));
    } else if (filters.intent === null) {
      setServerFilters(prev => ({ ...prev, intent: '' }));
    }
    
    // Update server sort
    if (sorter.field && sorter.order) {
      setServerFilters(prev => ({
        ...prev,
        sort_by: sorter.field,
        sort_order: sorter.order === 'ascend' ? 'asc' : 'desc'
      }));
    } else {
      // Reset to default sort
      setServerFilters(prev => ({
        ...prev,
        sort_by: 'created_at',
        sort_order: 'desc'
      }));
    }
  };

  const handleResetFilters = () => {
    setFilteredInfo({});
    setSortedInfo({});
    setCurrentPage(1); // Reset to page 1 when filters reset
    setServerFilters({
      user_message: '',
      bot_response: '',
      intent: '',
      sort_by: 'created_at',
      sort_order: 'desc'
    });
  };

  const getColumnSearchProps = (dataIndex, title) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
        <Input
          placeholder={`Search ${title}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => {
            confirm();
            setCurrentPage(1);
            setServerFilters(prev => ({ ...prev, user_message: selectedKeys[0] || '' }));
          }}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => {
              confirm();
              setCurrentPage(1);
              setServerFilters(prev => ({ ...prev, user_message: selectedKeys[0] || '' }));
            }}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            Search
          </Button>
          <Button
            onClick={() => {
              clearFilters && clearFilters();
              confirm({ closeDropdown: true });
              setCurrentPage(1);
              setServerFilters(prev => ({ ...prev, user_message: '' }));
            }}
            size="small"
            style={{ width: 90 }}
          >
            Reset
          </Button>
        </Space>
      </div>
    ),
    filteredValue: serverFilters.user_message ? [serverFilters.user_message] : null,
    filterIcon: filtered => (
      <SearchOutlined style={{ color: serverFilters.user_message ? '#1890ff' : undefined }} />
    ),
    // Client-side filtering disabled, handled by server
    onFilter: () => true,
  });

  const getColumnSearchPropsBot = (dataIndex, title) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
        <Input
          placeholder={`Search ${title}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => {
            confirm();
            setCurrentPage(1);
            setServerFilters(prev => ({ ...prev, bot_response: selectedKeys[0] || '' }));
          }}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => {
              confirm();
              setCurrentPage(1);
              setServerFilters(prev => ({ ...prev, bot_response: selectedKeys[0] || '' }));
            }}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            Search
          </Button>
          <Button
            onClick={() => {
              clearFilters && clearFilters();
              confirm({ closeDropdown: true });
              setCurrentPage(1);
              setServerFilters(prev => ({ ...prev, bot_response: '' }));
            }}
            size="small"
            style={{ width: 90 }}
          >
            Reset
          </Button>
        </Space>
      </div>
    ),
    filteredValue: serverFilters.bot_response ? [serverFilters.bot_response] : null,
    filterIcon: filtered => (
      <SearchOutlined style={{ color: serverFilters.bot_response ? '#1890ff' : undefined }} />
    ),
    // Client-side filtering disabled, handled by server
    onFilter: () => true,
  });

  const columns = useMemo(() => [
    {
      title: 'User Message',
      dataIndex: 'user_message',
      key: 'user_message',
      width: '30%',
      ellipsis: {
        showTitle: false,
      },
      sorter: true,
      sortOrder: sortedInfo.columnKey === 'user_message' ? sortedInfo.order : null,
      ...getColumnSearchProps('user_message', 'User Message'),
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: 'Bot Response',
      dataIndex: 'bot_response',
      key: 'bot_response',
      width: '30%',
      ellipsis: {
        showTitle: false,
      },
      sorter: true,
      sortOrder: sortedInfo.columnKey === 'bot_response' ? sortedInfo.order : null,
      ...getColumnSearchPropsBot('bot_response', 'Bot Response'),
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: 'Intent',
      dataIndex: 'intent',
      key: 'intent',
      width: '15%',
      filters: uniqueIntents.map(intent => ({ text: intent, value: intent })),
      filteredValue: filteredInfo.intent || null,
      onFilter: () => true, // Server-side filtering
      sorter: true,
      sortOrder: sortedInfo.columnKey === 'intent' ? sortedInfo.order : null,
      render: (text) => (
        <Tag color="blue">{text}</Tag>
      ),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: '15%',
      sorter: true,
      sortOrder: sortedInfo.columnKey === 'created_at' ? sortedInfo.order : null,
      defaultSortOrder: 'descend',
      render: (text) => new Date(text).toLocaleString('vi-VN'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: '10%',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Edit">
            <Button 
              size="small" 
              icon={<EditOutlined />}
              onClick={() => showEditModal(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Delete this training data?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Tooltip title="Delete">
              <Button size="small" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ], [sortedInfo, filteredInfo, uniqueIntents]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2}>Training</Title>
        <Space>
          <Button 
            icon={<DownloadOutlined />} 
            onClick={handleDownloadTemplate}
          >
            Download Template
          </Button>
          <Button 
            icon={<ExportOutlined />} 
            onClick={handleExport}
            disabled={!selectedBotId || trainingData.length === 0}
          >
            Export Data
          </Button>
        </Space>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%' }} direction="vertical">
          <Space>
            <strong>Select Bot: </strong>
            <Select
              style={{ width: 300 }}
              value={selectedBotId}
              onChange={setSelectedBotId}
              placeholder={bots.length === 0 ? "No bots available" : "Select a bot"}
              disabled={bots.length === 0}
              options={bots.map((bot) => ({
                label: bot.name,
                value: bot.id,
              }))}
            />
            <Button 
              type="primary"
              icon={<RocketOutlined />}
              onClick={handleTrain}
              disabled={!selectedBotId || bots.length === 0}
            >
              Train Bot
            </Button>
          </Space>

          {selectedBotId && (
            <Space>
              <Upload 
                beforeUpload={handleUpload} 
                accept=".json,.csv,.txt,.yml,.yaml,.md,.markdown" 
                maxCount={1}
                fileList={fileList}
                onChange={({ fileList }) => setFileList(fileList)}
              >
                <Button icon={<UploadOutlined />} type="primary">
                  Upload Training Data
                </Button>
              </Upload>
              <Button 
                icon={<PlusOutlined />} 
                type="primary"
                onClick={showAddModal}
              >
                Add New Data
              </Button>
              {(serverFilters.user_message || serverFilters.bot_response || serverFilters.intent) && (
                <Button 
                  onClick={handleResetFilters}
                  danger
                >
                  Clear All Filters
                </Button>
              )}
            </Space>
          )}

          <div style={{ fontSize: 12, color: '#666' }}>
            Supported formats: JSON, CSV, YAML, TXT, Markdown
          </div>
        </Space>
      </Card>

      {bots.length === 0 ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Title level={4} type="secondary">No bots available</Title>
            <p style={{ color: '#999', marginBottom: 16 }}>
              Please create a bot first from the "My Bots" page before you can add training data.
            </p>
          </div>
        </Card>
      ) : selectedBotId && (
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'data',
              label: (
                <span>
                  <EditOutlined style={{ marginRight: 8 }} />
                  Data
                </span>
              ),
              children: (
                <Card 
                  title={`Training Data (${trainingData.length} items)`}
                  extra={
                    selectedRowKeys.length > 0 && (
                      <Space>
                        <span style={{ marginRight: 8 }}>
                          Selected {selectedRowKeys.length} items
                        </span>
                        <Button 
                          icon={<ExportOutlined />}
                          onClick={handleExport}
                        >
                          Export Selected
                        </Button>
                        <Popconfirm
                          title={`Delete ${selectedRowKeys.length} selected items?`}
                          description="This action cannot be undone."
                          onConfirm={handleDeleteSelected}
                          okText="Yes"
                          cancelText="No"
                        >
                  <Button 
                    danger
                    icon={<DeleteOutlined />}
                  >
                    Delete Selected
                  </Button>
                </Popconfirm>
              </Space>
            )
          }
        >
          {loading ? (
            <div style={{ textAlign: 'center', padding: 50 }}>
              <Spin size="large" />
            </div>
          ) : (
            <Table
              rowSelection={rowSelection}
              columns={columns}
              dataSource={trainingData}
              rowKey="id"
              onChange={handleTableChange}
              pagination={{ 
                current: currentPage,
                pageSize: pageSize,
                showSizeChanger: true,
                showTotal: (total) => `Total ${total} items`,
                pageSizeOptions: ['10', '20', '50', '100'],
              }}
              bordered
            />
          )}
        </Card>
              ),
            },
            {
              key: 'history',
              label: (
                <span>
                  <HistoryOutlined style={{ marginRight: 8 }} />
                  History
                </span>
              ),
              children: (
                <Card>
                  <TrainingHistory 
                    botId={selectedBotId} 
                    refreshTrigger={refreshHistory}
                  />
                </Card>
              ),
            },
          ]}
        />
      )}

      {/* Training Progress Modal */}
      <TrainingProgressModal
        visible={trainingModalVisible}
        jobId={trainingJobId}
        onClose={() => {
          setTrainingModalVisible(false);
          setTrainingJobId(null);
        }}
        onComplete={(job) => {
          message.success('Training completed successfully!');
          setRefreshHistory(prev => prev + 1);
        }}
      />

      <Modal
        title={editingRecord ? 'Edit Training Data' : 'Add New Training Data'}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
        okText={editingRecord ? 'Update' : 'Add'}
      >
        <Form
          form={form}
          layout="vertical"
          name="trainingDataForm"
        >
          <Form.Item
            name="user_message"
            label="User Message"
            rules={[
              { required: true, message: 'Please input user message!' },
              { min: 2, message: 'Message must be at least 2 characters!' },
            ]}
          >
            <TextArea 
              rows={4} 
              placeholder="Enter user message..."
              showCount
              maxLength={10000}
            />
          </Form.Item>

          <Form.Item
            name="bot_response"
            label="Bot Response"
            rules={[
              { required: true, message: 'Please input bot response!' },
              { min: 2, message: 'Response must be at least 2 characters!' },
            ]}
          >
            <TextArea 
              rows={8} 
              placeholder="Enter bot response..."
              showCount
              maxLength={10000}
            />
          </Form.Item>

          <Form.Item
            name="intent"
            label="Intent"
            rules={[
              { required: true, message: 'Please input intent!' },
              { 
                pattern: /^[a-z0-9_]+$/, 
                message: 'Intent must contain only lowercase letters, numbers, and underscores!' 
              },
            ]}
          >
            <Input 
              placeholder="e.g., greeting, price_inquiry"
              showCount
              maxLength={200}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={
          previewMode === 'upload' 
            ? `Preview Upload Data (${previewData.length} items)`
            : `Add New Training Data (${previewData.length} items)`
        }
        open={isPreviewModalVisible}
        onOk={handleConfirmUpload}
        onCancel={handleCancelUpload}
        width={1100}
        okText={previewMode === 'upload' ? 'Upload' : 'Save All'}
        cancelText="Cancel"
        okButtonProps={{ loading }}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <Space>
              {previewMode === 'upload' && uploadFile && (
                <>
                  <Tag color="blue">{uploadFile.name}</Tag>
                  <span style={{ color: '#666' }}>
                    {previewData.length} items will be added
                  </span>
                </>
              )}
              {previewMode === 'add' && (
                <span style={{ color: '#666' }}>
                  {previewData.length} items ready to save
                </span>
              )}
            </Space>
            <Button 
              type="primary" 
              icon={<UploadOutlined />}
              onClick={handleConfirmUpload}
              loading={loading}
            >
              {previewMode === 'upload' ? 'Upload Now' : 'Save All'}
            </Button>
          </div>
          <Space>
            <Button 
              type="default" 
              size="small" 
              icon={<PlusOutlined />}
              onClick={handleAddPreviewRow}
            >
              Add Row
            </Button>
          </Space>
        </div>
        <Table
          columns={[
            {
              title: 'User Message',
              dataIndex: 'user',
              key: 'user',
              width: '30%',
              render: (text, record, index) => {
                if (editingPreviewKey === index) {
                  return (
                    <Input.TextArea
                      defaultValue={text}
                      autoSize={{ minRows: 2, maxRows: 4 }}
                      onChange={(e) => {
                        const newData = [...previewData];
                        newData[index] = { ...newData[index], user: e.target.value };
                        setPreviewData(newData);
                      }}
                    />
                  );
                }
                return text;
              },
            },
            {
              title: 'Bot Response',
              dataIndex: 'bot',
              key: 'bot',
              width: '30%',
              render: (text, record, index) => {
                if (editingPreviewKey === index) {
                  return (
                    <Input.TextArea
                      defaultValue={text}
                      autoSize={{ minRows: 2, maxRows: 4 }}
                      onChange={(e) => {
                        const newData = [...previewData];
                        newData[index] = { ...newData[index], bot: e.target.value };
                        setPreviewData(newData);
                      }}
                    />
                  );
                }
                return text;
              },
            },
            {
              title: 'Intent',
              dataIndex: 'intent',
              key: 'intent',
              width: '20%',
              render: (text, record, index) => {
                if (editingPreviewKey === index) {
                  return (
                    <Input
                      defaultValue={text}
                      onChange={(e) => {
                        const newData = [...previewData];
                        newData[index] = { ...newData[index], intent: e.target.value };
                        setPreviewData(newData);
                      }}
                    />
                  );
                }
                return <Tag color="blue">{text}</Tag>;
              },
            },
            {
              title: 'Actions',
              key: 'actions',
              width: '20%',
              render: (_, record, index) => {
                if (editingPreviewKey === index) {
                  return (
                    <Space size="small">
                      <Button
                        type="link"
                        size="small"
                        onClick={() => handleSavePreviewRow(index, previewData[index])}
                      >
                        Save
                      </Button>
                      <Button
                        type="link"
                        size="small"
                        onClick={handleCancelPreviewEdit}
                      >
                        Cancel
                      </Button>
                    </Space>
                  );
                }
                return (
                  <Space size="small">
                    <Button
                      type="link"
                      size="small"
                      icon={<EditOutlined />}
                      onClick={() => handleEditPreviewRow(index)}
                    >
                      Edit
                    </Button>
                    <Popconfirm
                      title="Delete this row?"
                      onConfirm={() => handleDeletePreviewRow(index)}
                      okText="Yes"
                      cancelText="No"
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
                  </Space>
                );
              },
            },
          ]}
          dataSource={previewData}
          rowKey={(record, index) => index}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} items`,
          }}
          size="small"
          bordered
        />
      </Modal>

      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {exportMode === 'template' ? (
              <>
                <DownloadOutlined style={{ fontSize: 20, color: '#1890ff' }} />
                <span>Select Template Format</span>
              </>
            ) : (
              <>
                <ExportOutlined style={{ fontSize: 20, color: '#1890ff' }} />
                <span>Select Export Format</span>
              </>
            )}
          </div>
        }
        open={isExportModalVisible}
        onCancel={() => setIsExportModalVisible(false)}
        footer={null}
        width={550}
        centered
      >
        <div style={{ 
          marginBottom: 24, 
          padding: '12px 16px',
          background: '#f0f5ff',
          borderRadius: 8,
          borderLeft: '4px solid #1890ff'
        }}>
          <p style={{ margin: 0, color: '#1890ff', fontWeight: 500 }}>
            {exportMode === 'template' ? (
              '📄 Download training data template with sample data'
            ) : (
              selectedRowKeys.length > 0 
                ? `📦 Exporting ${selectedRowKeys.length} selected ${selectedRowKeys.length === 1 ? 'item' : 'items'}`
                : `📦 Exporting all ${trainingData.length} ${trainingData.length === 1 ? 'item' : 'items'}`
            )}
          </p>
        </div>
        <Space direction="vertical" style={{ width: '100%' }} size={12}>
          <Button 
            block 
            size="large"
            onClick={() => handleExportWithFormat('json')}
            style={{ 
              textAlign: 'left', 
              height: 'auto', 
              padding: '16px 20px',
              border: '1px solid #d9d9d9',
              borderRadius: 8,
              transition: 'all 0.3s',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#1890ff';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(24,144,255,0.15)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#d9d9d9';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%' }}>
              <div style={{ 
                fontSize: 24, 
                width: 40, 
                height: 40, 
                flexShrink: 0,
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                background: '#f0f5ff',
                borderRadius: 8
              }}>
                📄
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>JSON</div>
                <div style={{ fontSize: 13, color: '#8c8c8c' }}>Standard JSON format with user, bot, and intent fields</div>
              </div>
            </div>
          </Button>
          <Button 
            block 
            size="large"
            onClick={() => handleExportWithFormat('csv')}
            style={{ 
              textAlign: 'left', 
              height: 'auto', 
              padding: '16px 20px',
              border: '1px solid #d9d9d9',
              borderRadius: 8,
              transition: 'all 0.3s',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#52c41a';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(82,196,26,0.15)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#d9d9d9';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%' }}>
              <div style={{ 
                fontSize: 24, 
                width: 40, 
                height: 40, 
                flexShrink: 0,
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                background: '#f6ffed',
                borderRadius: 8
              }}>
                📊
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>CSV</div>
                <div style={{ fontSize: 13, color: '#8c8c8c' }}>Comma-separated values, compatible with Excel</div>
              </div>
            </div>
          </Button>
          <Button 
            block 
            size="large"
            onClick={() => handleExportWithFormat('txt')}
            style={{ 
              textAlign: 'left', 
              height: 'auto', 
              padding: '16px 20px',
              border: '1px solid #d9d9d9',
              borderRadius: 8,
              transition: 'all 0.3s',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#722ed1';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(114,46,209,0.15)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#d9d9d9';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%' }}>
              <div style={{ 
                fontSize: 24, 
                width: 40, 
                height: 40, 
                flexShrink: 0,
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                background: '#f9f0ff',
                borderRadius: 8
              }}>
                📝
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Text</div>
                <div style={{ fontSize: 13, color: '#8c8c8c' }}>Plain text format with labels</div>
              </div>
            </div>
          </Button>
        </Space>
      </Modal>
    </div>
  );
};

export default TrainingDataPage;
