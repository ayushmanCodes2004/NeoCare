import React, { useEffect, useRef, useState } from 'react';
import WebRTCService from '../services/WebRTCService';
import SignalingService from '../services/SignalingService';
import './VideoCall.css';

function VideoCall({ userId, remoteUserId, setRemoteUserId }) {
  const [calleeId, setCalleeId] = useState('');
  const [inCall, setInCall] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioOnlyMode, setAudioOnlyMode] = useState(false);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const webrtcService = useRef(new WebRTCService());
  const signalingService = useRef(new SignalingService());

  useEffect(() => {
    connectToSignaling();
    return () => cleanup();
  }, []);

  const connectToSignaling = async () => {
    try {
      // Only connect to signaling server, don't access camera yet
      await signalingService.current.connect(userId, handleSignalMessage);
    } catch (error) {
      console.error('Signaling connection error:', error);
      alert('Failed to connect to signaling server');
    }
  };

  const initializeMedia = async (audioOnly = false) => {
    try {
      // Get local media
      const stream = await webrtcService.current.initializeMedia(audioOnly);
      if (localVideoRef.current && !audioOnly) {
        localVideoRef.current.srcObject = stream;
      }
      return true;
    } catch (error) {
      console.error('Media initialization error:', error);
      
      // If video fails, try audio-only mode
      if (!audioOnly && error.message.includes('in use')) {
        console.log('Camera in use, trying audio-only mode...');
        const audioOnlyResult = await initializeMedia(true);
        if (audioOnlyResult) {
          setAudioOnlyMode(true);
          alert('Camera is in use. Joining with audio only.');
          return true;
        }
      }
      
      alert(error.message || 'Failed to access camera/microphone. Please check your device permissions.');
      return false;
    }
  };

  const handleSignalMessage = async (signal) => {
    const { type, from, data } = signal;
    console.log('Received signal:', type, 'from:', from);

    switch (type) {
      case 'offer':
        // Initialize media when receiving a call
        console.log('Receiving call from:', from);
        const mediaReady = await initializeMedia();
        if (!mediaReady) {
          console.error('Failed to initialize media for incoming call');
          alert('Cannot answer call: Unable to access camera/microphone. Please use a different browser or close other tabs using the camera.');
          return;
        }

        setRemoteUserId(from);
        setInCall(true);
        webrtcService.current.createPeerConnection(
          (candidate) => {
            console.log('Sending ICE candidate to:', from);
            signalingService.current.sendSignal('ice-candidate', from, candidate);
          },
          (stream) => {
            console.log('Received remote stream');
            if (remoteVideoRef.current) {
              remoteVideoRef.current.srcObject = stream;
            }
          }
        );
        await webrtcService.current.handleOffer(data);
        const answer = await webrtcService.current.createAnswer();
        signalingService.current.sendSignal('answer', from, answer);
        break;

      case 'answer':
        console.log('Received answer from:', from);
        await webrtcService.current.handleAnswer(data);
        break;

      case 'ice-candidate':
        console.log('Received ICE candidate from:', from);
        await webrtcService.current.addIceCandidate(data);
        break;

      default:
        break;
    }
  };

  const startCall = async () => {
    if (!calleeId.trim()) {
      alert('Please enter a user ID to call');
      return;
    }

    console.log('Starting call to:', calleeId);
    
    // Initialize media when starting a call
    const mediaReady = await initializeMedia();
    if (!mediaReady) return;

    setRemoteUserId(calleeId);
    setInCall(true);

    webrtcService.current.createPeerConnection(
      (candidate) => {
        console.log('Sending ICE candidate to:', calleeId);
        signalingService.current.sendSignal('ice-candidate', calleeId, candidate);
      },
      (stream) => {
        console.log('Received remote stream');
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = stream;
        }
      }
    );

    const offer = await webrtcService.current.createOffer();
    console.log('Sending offer to:', calleeId);
    signalingService.current.sendSignal('offer', calleeId, offer);
  };

  const endCall = () => {
    webrtcService.current.closeConnection();
    if (localVideoRef.current) {
      localVideoRef.current.srcObject = null;
    }
    if (remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = null;
    }
    setInCall(false);
    setRemoteUserId('');
    setCalleeId('');
  };

  const toggleAudio = () => {
    const newState = !audioEnabled;
    webrtcService.current.toggleAudio(newState);
    setAudioEnabled(newState);
  };

  const toggleVideo = () => {
    const newState = !videoEnabled;
    webrtcService.current.toggleVideo(newState);
    setVideoEnabled(newState);
  };

  const cleanup = () => {
    webrtcService.current.closeConnection();
    signalingService.current.disconnect();
  };

  return (
    <div className="video-call-container">
      <div className="header">
        <h2>User: {userId}</h2>
        {inCall && <span className="status">In call with: {remoteUserId}</span>}
      </div>

      <div className="video-grid">
        <div className="video-wrapper">
          {audioOnlyMode ? (
            <div className="audio-only-placeholder">
              <div className="audio-icon">🎤</div>
              <p>Audio Only</p>
            </div>
          ) : (
            <video ref={localVideoRef} autoPlay muted playsInline className="video local-video" />
          )}
          <span className="video-label">You</span>
        </div>
        <div className="video-wrapper">
          <video ref={remoteVideoRef} autoPlay playsInline className="video remote-video" />
          <span className="video-label">{remoteUserId || 'Waiting...'}</span>
        </div>
      </div>

      <div className="controls">
        {!inCall ? (
          <div className="call-input">
            <input
              type="text"
              placeholder="Enter user ID to call"
              value={calleeId}
              onChange={(e) => setCalleeId(e.target.value)}
              className="input"
            />
            <button onClick={startCall} className="btn btn-primary">
              Start Call
            </button>
          </div>
        ) : (
          <div className="call-controls">
            <button onClick={toggleAudio} className={`btn ${audioEnabled ? 'btn-secondary' : 'btn-danger'}`}>
              {audioEnabled ? '🎤 Mute' : '🎤 Unmute'}
            </button>
            <button onClick={toggleVideo} className={`btn ${videoEnabled ? 'btn-secondary' : 'btn-danger'}`}>
              {videoEnabled ? '📹 Stop Video' : '📹 Start Video'}
            </button>
            <button onClick={endCall} className="btn btn-danger">
              End Call
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoCall;
