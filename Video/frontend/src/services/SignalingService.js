import SockJS from 'sockjs-client';
import Stomp from 'stompjs';

class SignalingService {
  constructor() {
    this.stompClient = null;
    this.userId = null;
    this.connected = false;
  }

  connect(userId, onMessageReceived) {
    this.userId = userId;
    const socket = new SockJS('http://localhost:8080/ws');
    this.stompClient = Stomp.over(socket);

    return new Promise((resolve, reject) => {
      this.stompClient.connect({}, 
        () => {
          this.connected = true;
          // Subscribe to personal queue for incoming signals
          this.stompClient.subscribe(`/queue/signal/${userId}`, (message) => {
            const signal = JSON.parse(message.body);
            onMessageReceived(signal);
          });
          resolve();
        },
        (error) => {
          this.connected = false;
          reject(error);
        }
      );
    });
  }

  sendSignal(type, to, data) {
    if (this.stompClient && this.connected) {
      const message = {
        type,
        from: this.userId,
        to,
        data
      };
      this.stompClient.send('/app/signal', {}, JSON.stringify(message));
    }
  }

  disconnect() {
    if (this.stompClient && this.connected) {
      try {
        this.stompClient.disconnect();
      } catch (error) {
        console.warn('Error disconnecting:', error);
      }
      this.connected = false;
    }
  }
}

export default SignalingService;
