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
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import { botsAPI } from '../api/bots';

const { Title, Text } = Typography;

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
  const messagesEndRef = useRef(null);
  const streamingIntervalRef = useRef(null);

  // Create new session when bot changes
  useEffect(() => {
    if (selectedBotId) {
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
    console.log('[Session] Created new session:', newSessionId);
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
      const response = await botsAPI.chatWithBot(selectedBotId, inputValue, sessionId);
      
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
        <Card
          title={
            <Space>
              <RobotOutlined />
              <span>{selectedBot?.name || 'Bot'}</span>
            </Space>
          }
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
      ) : (
        <Empty description="No active bots available. Please train a bot first." />
      )}
    </div>
  );
};

export default ChatPage;
