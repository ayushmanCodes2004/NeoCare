/**
 * WebRTC Manager for Video Consultation
 * Simplified version using WebSocket for signaling
 */

const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
  ]
};

export class WebRTCManager {
  private consultationId: string;
  private isDoctor: boolean;
  private onRemoteStream: (stream: MediaStream) => void;
  private onConnectionStateChange: (state: string) => void;
  
  private peerConnection: RTCPeerConnection | null = null;
  private localStream: MediaStream | null = null;
  private remoteStream: MediaStream | null = null;
  private ws: WebSocket | null = null;
  private iceCandidateQueue: RTCIceCandidateInit[] = [];

  constructor(
    consultationId: string,
    isDoctor: boolean,
    onRemoteStream: (stream: MediaStream) => void,
    onConnectionStateChange: (state: string) => void
  ) {
    this.consultationId = consultationId;
    this.isDoctor = isDoctor;
    this.onRemoteStream = onRemoteStream;
    this.onConnectionStateChange = onConnectionStateChange;
  }

  /**
   * Initialize WebRTC connection
   */
  async initialize(): Promise<MediaStream> {
    try {
      // Get local media stream
      this.localStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // Create peer connection
      this.peerConnection = new RTCPeerConnection(ICE_SERVERS);

      // Add local tracks to peer connection
      this.localStream.getTracks().forEach(track => {
        this.peerConnection!.addTrack(track, this.localStream!);
      });

      // Handle remote stream
      this.peerConnection.ontrack = (event) => {
        if (!this.remoteStream) {
          this.remoteStream = new MediaStream();
          this.onRemoteStream(this.remoteStream);
        }
        this.remoteStream.addTrack(event.track);
      };

      // Handle ICE candidates
      this.peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.sendSignal({
            type: 'ice-candidate',
            candidate: event.candidate
          });
        }
      };

      // Handle connection state changes
      this.peerConnection.onconnectionstatechange = () => {
        const state = this.peerConnection!.connectionState;
        console.log('Connection state:', state);
        this.onConnectionStateChange(state);
      };

      // Connect to signaling server
      await this.connectSignaling();

      return this.localStream;
    } catch (error) {
      console.error('Failed to initialize WebRTC:', error);
      throw error;
    }
  }

  /**
   * Connect to WebSocket signaling server
   * Using SockJS fallback for better compatibility
   */
  private async connectSignaling(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Try WebSocket first, fallback to polling
      const wsUrl = 'ws://localhost:8080/ws/consultation';
      const httpUrl = 'http://localhost:8080/ws/consultation';
      
      try {
        this.ws = new WebSocket(wsUrl);
      } catch (error) {
        console.warn('WebSocket not available, using HTTP fallback');
        // For now, just reject - we'll add proper SockJS client later
        reject(new Error('WebSocket not supported'));
        return;
      }

      let connectionTimeout = setTimeout(() => {
        if (this.ws && this.ws.readyState !== WebSocket.OPEN) {
          this.ws.close();
          reject(new Error('Connection timeout'));
        }
      }, 10000); // 10 second timeout

      this.ws.onopen = () => {
        clearTimeout(connectionTimeout);
        console.log('Signaling connected');
        
        // Send join message
        this.sendSignal({
          type: 'join',
          consultationId: this.consultationId,
          role: this.isDoctor ? 'doctor' : 'worker'
        });

        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleSignal(message);
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };

      this.ws.onerror = (error) => {
        clearTimeout(connectionTimeout);
        console.error('WebSocket error:', error);
        reject(new Error('Signaling connection failed'));
      };

      this.ws.onclose = () => {
        clearTimeout(connectionTimeout);
        console.log('Signaling disconnected');
        this.onConnectionStateChange('disconnected');
      };
    });
  }

  /**
   * Handle incoming signaling messages
   */
  private async handleSignal(message: any): Promise<void> {
    try {
      switch (message.type) {
        case 'offer':
          await this.handleOffer(message.offer);
          break;
        
        case 'answer':
          await this.handleAnswer(message.answer);
          break;
        
        case 'ice-candidate':
          await this.handleIceCandidate(message.candidate);
          break;
        
        case 'user-joined':
          // Other user joined, doctor should create offer
          if (this.isDoctor && message.role === 'worker') {
            setTimeout(() => this.createOffer(), 1000);
          }
          break;
        
        case 'user-left':
          this.onConnectionStateChange('disconnected');
          break;
      }
    } catch (error) {
      console.error('Error handling signal:', error);
    }
  }

  /**
   * Create and send offer (doctor initiates)
   */
  private async createOffer(): Promise<void> {
    try {
      const offer = await this.peerConnection!.createOffer();
      await this.peerConnection!.setLocalDescription(offer);
      
      this.sendSignal({
        type: 'offer',
        offer: offer
      });
    } catch (error) {
      console.error('Error creating offer:', error);
    }
  }

  /**
   * Handle incoming offer (worker receives)
   */
  private async handleOffer(offer: RTCSessionDescriptionInit): Promise<void> {
    try {
      await this.peerConnection!.setRemoteDescription(new RTCSessionDescription(offer));
      
      const answer = await this.peerConnection!.createAnswer();
      await this.peerConnection!.setLocalDescription(answer);
      
      this.sendSignal({
        type: 'answer',
        answer: answer
      });

      // Process queued ICE candidates
      while (this.iceCandidateQueue.length > 0) {
        const candidate = this.iceCandidateQueue.shift()!;
        await this.peerConnection!.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  }

  /**
   * Handle incoming answer (doctor receives)
   */
  private async handleAnswer(answer: RTCSessionDescriptionInit): Promise<void> {
    try {
      await this.peerConnection!.setRemoteDescription(new RTCSessionDescription(answer));
      
      // Process queued ICE candidates
      while (this.iceCandidateQueue.length > 0) {
        const candidate = this.iceCandidateQueue.shift()!;
        await this.peerConnection!.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  }

  /**
   * Handle incoming ICE candidate
   */
  private async handleIceCandidate(candidate: RTCIceCandidateInit): Promise<void> {
    try {
      if (this.peerConnection!.remoteDescription) {
        await this.peerConnection!.addIceCandidate(new RTCIceCandidate(candidate));
      } else {
        // Queue candidates until remote description is set
        this.iceCandidateQueue.push(candidate);
      }
    } catch (error) {
      console.error('Error handling ICE candidate:', error);
    }
  }

  /**
   * Send signaling message via WebSocket
   */
  private sendSignal(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Toggle video track
   */
  toggleVideo(enabled: boolean): void {
    if (this.localStream) {
      this.localStream.getVideoTracks().forEach(track => {
        track.enabled = enabled;
      });
    }
  }

  /**
   * Toggle audio track
   */
  toggleAudio(enabled: boolean): void {
    if (this.localStream) {
      this.localStream.getAudioTracks().forEach(track => {
        track.enabled = enabled;
      });
    }
  }

  /**
   * Cleanup and close connection
   */
  cleanup(): void {
    // Send leave message
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.sendSignal({
        type: 'leave',
        consultationId: this.consultationId,
        role: this.isDoctor ? 'doctor' : 'worker'
      });
    }

    // Stop local tracks
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
    }

    // Close peer connection
    if (this.peerConnection) {
      this.peerConnection.close();
    }

    // Close WebSocket
    if (this.ws) {
      this.ws.close();
    }

    this.localStream = null;
    this.remoteStream = null;
    this.peerConnection = null;
    this.ws = null;
  }
}
