/**
 * WebRTC Utility for Video Consultation
 * Handles peer connection, media streams, and STOMP signaling
 */

import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';

const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
  ]
};

export class WebRTCManager {
  constructor(consultationId, isDoctor, onRemoteStream, onConnectionStateChange) {
    this.consultationId = consultationId;
    this.isDoctor = isDoctor;
    this.onRemoteStream = onRemoteStream;
    this.onConnectionStateChange = onConnectionStateChange;
    
    this.peerConnection = null;
    this.localStream = null;
    this.remoteStream = null;
    this.stompClient = null;
    this.iceCandidateQueue = [];
  }

  /**
   * Initialize WebRTC connection
   */
  async initialize() {
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
        this.peerConnection.addTrack(track, this.localStream);
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
        const state = this.peerConnection.connectionState;
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
   * Connect to STOMP WebSocket signaling server
   */
  async connectSignaling() {
    return new Promise((resolve, reject) => {
      const wsUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
      const socket = new SockJS(`${wsUrl}/ws/consultation`);
      
      this.stompClient = new Client({
        webSocketFactory: () => socket,
        debug: (str) => console.log('STOMP:', str),
        reconnectDelay: 5000,
        heartbeatIncoming: 4000,
        heartbeatOutgoing: 4000,
      });

      this.stompClient.onConnect = () => {
        console.log('Signaling connected');
        
        // Subscribe to consultation topic
        this.stompClient.subscribe(
          `/topic/consultation/${this.consultationId}`,
          (message) => {
            const signal = JSON.parse(message.body);
            this.handleSignal(signal);
          }
        );

        // Send join message
        this.stompClient.publish({
          destination: `/app/consultation/${this.consultationId}/join`,
          body: JSON.stringify({
            role: this.isDoctor ? 'doctor' : 'patient',
            consultationId: this.consultationId
          })
        });

        resolve();
      };

      this.stompClient.onStompError = (frame) => {
        console.error('STOMP error:', frame);
        reject(new Error('Signaling connection failed'));
      };

      this.stompClient.activate();
    });
  }

  /**
   * Handle incoming signaling messages
   */
  async handleSignal(message) {
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
          if (this.isDoctor && message.role === 'patient') {
            // Small delay to ensure both peers are ready
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
  async createOffer() {
    try {
      const offer = await this.peerConnection.createOffer();
      await this.peerConnection.setLocalDescription(offer);
      
      this.sendSignal({
        type: 'offer',
        offer: offer
      });
    } catch (error) {
      console.error('Error creating offer:', error);
    }
  }

  /**
   * Handle incoming offer (patient receives)
   */
  async handleOffer(offer) {
    try {
      await this.peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
      
      const answer = await this.peerConnection.createAnswer();
      await this.peerConnection.setLocalDescription(answer);
      
      this.sendSignal({
        type: 'answer',
        answer: answer
      });

      // Process queued ICE candidates
      while (this.iceCandidateQueue.length > 0) {
        const candidate = this.iceCandidateQueue.shift();
        await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  }

  /**
   * Handle incoming answer (doctor receives)
   */
  async handleAnswer(answer) {
    try {
      await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
      
      // Process queued ICE candidates
      while (this.iceCandidateQueue.length > 0) {
        const candidate = this.iceCandidateQueue.shift();
        await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
      }
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  }

  /**
   * Handle incoming ICE candidate
   */
  async handleIceCandidate(candidate) {
    try {
      if (this.peerConnection.remoteDescription) {
        await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
      } else {
        // Queue candidates until remote description is set
        this.iceCandidateQueue.push(candidate);
      }
    } catch (error) {
      console.error('Error handling ICE candidate:', error);
    }
  }

  /**
   * Send signaling message via STOMP
   */
  sendSignal(message) {
    if (this.stompClient && this.stompClient.connected) {
      this.stompClient.publish({
        destination: `/app/consultation/${this.consultationId}/signal`,
        body: JSON.stringify(message)
      });
    }
  }

  /**
   * Toggle video track
   */
  toggleVideo(enabled) {
    if (this.localStream) {
      this.localStream.getVideoTracks().forEach(track => {
        track.enabled = enabled;
      });
    }
  }

  /**
   * Toggle audio track
   */
  toggleAudio(enabled) {
    if (this.localStream) {
      this.localStream.getAudioTracks().forEach(track => {
        track.enabled = enabled;
      });
    }
  }

  /**
   * Get connection statistics
   */
  async getStats() {
    if (this.peerConnection) {
      const stats = await this.peerConnection.getStats();
      return stats;
    }
    return null;
  }

  /**
   * Cleanup and close connection
   */
  cleanup() {
    // Send leave message
    if (this.stompClient && this.stompClient.connected) {
      this.stompClient.publish({
        destination: `/app/consultation/${this.consultationId}/leave`,
        body: JSON.stringify({
          role: this.isDoctor ? 'doctor' : 'patient',
          consultationId: this.consultationId
        })
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

    // Disconnect STOMP client
    if (this.stompClient) {
      this.stompClient.deactivate();
    }

    this.localStream = null;
    this.remoteStream = null;
    this.peerConnection = null;
    this.stompClient = null;
  }
}
