import { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Typography, 
  Spin,
  Empty 
} from 'antd';
import {
  RobotOutlined,
  MessageOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { botsAPI } from '../api/bots';

const { Title } = Typography;

const DashboardHome = () => {
  const [loading, setLoading] = useState(true);
  const [bots, setBots] = useState([]);

  useEffect(() => {
    loadBots();
  }, []);

  const loadBots = async () => {
    try {
      const data = await botsAPI.getAllBots();
      setBots(data);
    } catch (error) {
      console.error('Failed to load bots:', error);
    } finally {
      setLoading(false);
    }
  };

  const activeBots = bots.filter(bot => bot.status === 'active').length;
  const totalTrainingData = bots.reduce((sum, bot) => sum + (bot.training_count || 0), 0);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Bots"
              value={bots.length}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Bots"
              value={activeBots}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Training Data"
              value={totalTrainingData}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Conversations"
              value={0}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Recent Bots">
        {bots.length === 0 ? (
          <Empty description="Chưa có bot nào. Hãy tạo bot đầu tiên!" />
        ) : (
          <Row gutter={16}>
            {bots.slice(0, 4).map(bot => (
              <Col xs={24} sm={12} lg={6} key={bot.id}>
                <Card size="small" style={{ marginBottom: 16 }}>
                  <Title level={5}>{bot.name}</Title>
                  <p style={{ color: '#666', fontSize: 12 }}>
                    {bot.description || 'No description'}
                  </p>
                  <div style={{ fontSize: 12 }}>
                    Status: <strong>{bot.status}</strong>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Card>
    </div>
  );
};

export default DashboardHome;
