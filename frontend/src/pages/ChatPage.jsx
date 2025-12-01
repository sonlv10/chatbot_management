import { useState, useEffect, useRef } from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Avatar,
  Typography,
  Space,
  Select,
  message,
  Empty,
  Layout,
  Badge,
  Tooltip,
  Spin,
  Switch,
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  PlusOutlined,
  DeleteOutlined,
  MessageOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { botsAPI } from '../api/bots';
import axios from '../api/axios';

const { Title, Text } = Typography;
const { Sider, Content } = Layout;

const ChatPage = () => {
  // Add cursor blink animation style
  const cursorStyle = `
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
  `;

  const { botId: urlBotId } = useParams();
  const [bots, setBots] = useState([]);
  const [selectedBotId, setSelectedBotId] = useState(urlBotId || null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [isSave, setIsSave] = useState(() => {
    const saved = localStorage.getItem('chatIsSave');
    return saved !== null ? JSON.parse(saved) : true;
  });
  const messagesEndRef = useRef(null);
  const streamingIntervalRef = useRef(null);

  // Create new session when bot changes
  useEffect(() => {
    if (selectedBotId) {
      loadConversations();
      createNewSession();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedBotId]);

  useEffect(() => {
    loadBots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (urlBotId) {
      setSelectedBotId(parseInt(urlBotId));
    }
  }, [urlBotId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Save isSave to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('chatIsSave', JSON.stringify(isSave));
  }, [isSave]);

  useEffect(() => {
    return () => {
      if (streamingIntervalRef.current) {
        clearInterval(streamingIntervalRef.current);
      }
    };
  }, []);

  const loadBots = async () => {
    try {
      const data = await botsAPI.getAllBots();
      // Allow both 'active' and 'trained' bots for chat
      const activeBots = data.filter((bot) => bot.status === 'active' || bot.status === 'trained');
      setBots(activeBots);
      
      if (activeBots.length > 0 && !selectedBotId) {
        setSelectedBotId(activeBots[0].id);
      }
    } catch (err) {
      message.error('Failed to load bots');
      console.error('Load bots error:', err);
    }
  };

  const createNewSession = () => {
    // Generate unique session ID
    const newSessionId = `session_${selectedBotId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    setMessages([]); // Clear messages for new session
    setSelectedConversationId(null);
    console.log('[Session] Created new session:', newSessionId);
  };

  const loadConversations = async () => {
    if (!selectedBotId) return;
    
    setLoadingConversations(true);
    try {
      const response = await axios.get(`api/conversations/bot/${selectedBotId}/history?limit=50`);
      const convs = response.data;
      setConversations(convs);
      
      // If we have a sessionId but no selectedConversationId, find and select the matching conversation
      if (sessionId && !selectedConversationId && convs.length > 0) {
        const matchingConv = convs.find(c => c.session_id === sessionId);
        if (matchingConv) {
          setSelectedConversationId(matchingConv.conversation_id);
        }
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (conversationId) => {
    try {
      const response = await axios.get(`api/conversations/${conversationId}`);
      const conv = response.data;
      
      // Set session ID from conversation
      setSessionId(conv.session_id);
      setSelectedConversationId(conversationId);
      
      // Convert conversation messages to chat messages format
      const chatMessages = conv.messages.map((msg) => ({
        id: msg.id,
        type: msg.sender,
        content: msg.message,
        intent: msg.intent,
        confidence: msg.confidence,
        timestamp: new Date(msg.timestamp).toLocaleTimeString(),
      }));
      
      setMessages(chatMessages);
    } catch (err) {
      message.error('Failed to load conversation');
      console.error('Load conversation error:', err);
    }
  };

  const deleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    
    try {
      await axios.delete(`api/conversations/${conversationId}`);
      message.success('Conversation deleted');
      
      // Reload conversations list
      await loadConversations();
      
      // If deleted conversation was selected, create new session
      if (selectedConversationId === conversationId) {
        createNewSession();
      }
    } catch (err) {
      message.error('Failed to delete conversation');
      console.error('Delete conversation error:', err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim() || !selectedBotId) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages([...messages, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await botsAPI.chatWithBot(selectedBotId, inputValue, sessionId, isSave);
      
      // If this is the first message in a new session and saving is enabled, reload conversations
      if (isSave && messages.length === 0 && !selectedConversationId) {
        setTimeout(() => {
          loadConversations();
        }, 500); // Small delay to ensure backend has created the conversation
      }
      
      // Start streaming effect
      setIsStreaming(true);
      setStreamingMessage('');
      
      const fullMessage = response.message;
      let currentIndex = 0;
      
      // Clear any existing interval
      if (streamingIntervalRef.current) {
        clearInterval(streamingIntervalRef.current);
      }
      
      // Stream characters one by one
      streamingIntervalRef.current = setInterval(() => {
        if (currentIndex < fullMessage.length) {
          setStreamingMessage(fullMessage.substring(0, currentIndex + 1));
          currentIndex++;
        } else {
          // Streaming complete
          clearInterval(streamingIntervalRef.current);
          setIsStreaming(false);
          setStreamingMessage('');
          
          const botMessage = {
            id: Date.now() + 1,
            type: 'bot',
            content: response.message,
            intent: response.intent,
            confidence: response.confidence,
            timestamp: new Date().toLocaleTimeString(),
          };
          
          setMessages((prev) => [...prev, botMessage]);
        }
      }, 20); // 20ms per character
      
    } catch (err) {
      message.error(err?.response?.data?.detail || 'Failed to send message');
      setIsStreaming(false);
      setStreamingMessage('');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const selectedBot = bots.find((bot) => bot.id === selectedBotId);

  return (
    <div>
      <style>{cursorStyle}</style>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2}>Test Chat</Title>
        <Space>
          <Tooltip title={isSave ? "Conversation will be saved" : "Conversation won't be saved"}>
            <Space>
              <SaveOutlined style={{ color: isSave ? '#52c41a' : '#d9d9d9' }} />
              <Text>Save to DB:</Text>
              <Switch 
                checked={isSave} 
                onChange={setIsSave}
                checkedChildren="ON"
                unCheckedChildren="OFF"
              />
            </Space>
          </Tooltip>
          <Text>Select Bot:</Text>
          <Select
            style={{ width: 250 }}
            value={selectedBotId}
            onChange={(value) => {
              setSelectedBotId(value);
              setMessages([]);
            }}
            options={bots.map((bot) => ({
              label: `${bot.name} (${bot.language})`,
              value: bot.id,
            }))}
          />
        </Space>
      </div>

      {selectedBotId ? (
        <Layout style={{ background: '#fff', minHeight: 600 }}>
          {/* Conversation List Sidebar */}
          <Sider width={280} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
            <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                block
                onClick={createNewSession}
              >
                New Conversation
              </Button>
            </div>
            
            <div style={{ padding: '8px 0', maxHeight: 'calc(100vh - 300px)', overflowY: 'auto' }}>
              {loadingConversations ? (
                <div style={{ textAlign: 'center', padding: 20 }}>
                  <Spin />
                </div>
              ) : conversations.length === 0 ? (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="No conversations yet"
                  style={{ marginTop: 50 }}
                />
              ) : (
                <List
                  dataSource={conversations}
                  renderItem={(conv) => (
                    <List.Item
                      key={conv.conversation_id}
                      style={{
                        cursor: 'pointer',
                        padding: '12px 16px',
                        background: selectedConversationId === conv.conversation_id ? '#e6f7ff' : 'transparent',
                        borderLeft: selectedConversationId === conv.conversation_id ? '3px solid #1890ff' : '3px solid transparent',
                      }}
                      onClick={() => loadConversationMessages(conv.conversation_id)}
                      actions={[
                        <Tooltip title="Delete" key="delete">
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={(e) => deleteConversation(conv.conversation_id, e)}
                          />
                        </Tooltip>
                      ]}
                    >
                      <List.Item.Meta
                        avatar={<Avatar icon={<MessageOutlined />} />}
                        title={
                          <Space>
                            <Text ellipsis style={{ maxWidth: 150 }}>
                              {conv.preview || 'New conversation'}
                            </Text>
                            <Badge count={conv.message_count} />
                          </Space>
                        }
                        description={
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            {new Date(conv.started_at).toLocaleDateString()} {new Date(conv.started_at).toLocaleTimeString()}
                          </Text>
                        }
                      />
                    </List.Item>
                  )}
                />
              )}
            </div>
          </Sider>

          {/* Chat Content */}
          <Content style={{ padding: 0 }}>
            <Card
              title={
                <Space>
                  <RobotOutlined />
                  <span>{selectedBot?.name || 'Bot'}</span>
                  {selectedConversationId && (
                    <Badge status="processing" text="Active conversation" />
                  )}
                </Space>
              }
              bordered={false}
            >
          <div
            style={{
              height: 500,
              overflowY: 'auto',
              marginBottom: 16,
              padding: 16,
              background: '#f5f5f5',
              borderRadius: 8,
            }}
          >
            {messages.length === 0 && !isStreaming ? (
              <Empty
                description="Start chatting with your bot"
                style={{ marginTop: 150 }}
              />
            ) : (
              <>
                <List
                  dataSource={messages}
                  renderItem={(item) => (
                    <List.Item
                      style={{
                        justifyContent: item.type === 'user' ? 'flex-end' : 'flex-start',
                        border: 'none',
                      }}
                    >
                      <div
                        style={{
                          maxWidth: '70%',
                          display: 'flex',
                          gap: 8,
                          flexDirection: item.type === 'user' ? 'row-reverse' : 'row',
                        }}
                      >
                        <Avatar
                          icon={item.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                          style={{
                            backgroundColor: item.type === 'user' ? '#1890ff' : '#52c41a',
                          }}
                        />
                        <div>
                          <div
                            style={{
                              padding: '8px 12px',
                              borderRadius: 8,
                              background: item.type === 'user' ? '#1890ff' : '#fff',
                              color: item.type === 'user' ? '#fff' : '#000',
                              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-word',
                            }}
                          >
                            {item.content}
                          </div>
                          <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                            {item.timestamp}
                            {item.intent && ` • ${item.intent}`}
                            {item.confidence && ` • ${(item.confidence * 100).toFixed(1)}%`}
                          </div>
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
                
                {isStreaming && (
                  <List.Item
                    style={{
                      justifyContent: 'flex-start',
                      border: 'none',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '70%',
                        display: 'flex',
                        gap: 8,
                      }}
                    >
                      <Avatar
                        icon={<RobotOutlined />}
                        style={{ backgroundColor: '#52c41a' }}
                      />
                      <div>
                        <div
                          style={{
                            padding: '8px 12px',
                            borderRadius: 8,
                            background: '#fff',
                            color: '#000',
                            boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                          }}
                        >
                          {streamingMessage}
                          <span style={{ animation: 'blink 1s infinite' }}>▋</span>
                        </div>
                      </div>
                    </div>
                  </List.Item>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          <Space.Compact style={{ width: '100%' }}>
            <Input.TextArea
              placeholder="Type your message... (Shift+Enter for newline)"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading || isStreaming}
              size="large"
              autoSize={{ minRows: 1, maxRows: 4 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
              disabled={isStreaming}
              size="large"
            >
              Send
            </Button>
          </Space.Compact>
        </Card>
          </Content>
        </Layout>
      ) : (
        <Empty description="No active bots available. Please train a bot first." />
      )}
    </div>
  );
};

export default ChatPage;
