import io from 'socket.io-client';

class RasaSocketClient {
  constructor() {
    this.socket = null;
    this.sessionId = null;
    this.messageCallback = null;
    this.typingCallback = null;
  }

  connect(botId, sessionId) {
    this.sessionId = sessionId;
    
    // Kết nối đến Rasa SocketIO server
    this.socket = io('http://localhost:5005', {
      path: '/socket.io/',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    // Lắng nghe kết nối thành công
    this.socket.on('connect', () => {
      console.log('✅ Connected to Rasa SocketIO');
      
      // Gửi session_request để bắt đầu conversation
      this.socket.emit('session_request', {
        session_id: this.sessionId,
      });
    });

    // Lắng nghe tin nhắn từ bot
    this.socket.on('bot_uttered', (message) => {
      console.log('📨 Bot message:', message);
      if (this.messageCallback) {
        this.messageCallback({
          text: message.text,
          timestamp: new Date().toISOString(),
        });
      }
    });

    // Lắng nghe typing indicator
    this.socket.on('bot_typing', () => {
      console.log('⌨️ Bot is typing...');
      if (this.typingCallback) {
        this.typingCallback(true);
      }
    });

    // Lắng nghe lỗi
    this.socket.on('connect_error', (error) => {
      console.error('❌ Connection error:', error);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 Disconnected:', reason);
    });
  }

  sendMessage(message) {
    if (!this.socket || !this.socket.connected) {
      console.error('Socket not connected');
      return;
    }

    // Gửi tin nhắn đến Rasa
    this.socket.emit('user_uttered', {
      message: message,
      session_id: this.sessionId,
    });
  }

  onMessage(callback) {
    this.messageCallback = callback;
  }

  onTyping(callback) {
    this.typingCallback = callback;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export default new RasaSocketClient();
