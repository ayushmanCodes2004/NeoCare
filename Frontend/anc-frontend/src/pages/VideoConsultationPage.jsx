import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Video, VideoOff, Mic, MicOff, PhoneOff, Wifi, WifiOff } from 'lucide-react';
import axios from 'axios';
import { WebRTCManager } from '../utils/webrtc';
import '../styles/dashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Video Consultation Page - WebRTC-based video consultation
 */
export default function VideoConsultationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [consultation, setConsultation] = useState(null);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [callStarted, setCallStarted] = useState(false);
  const [connectionState, setConnectionState] = useState('new');
  const [error, setError] = useState(null);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const webrtcManager = useRef(null);

  useEffect(() => {
    const fetchConsultation = async () => {
      try {
        const token = localStorage.getItem('anc_token');
        const response = await axios.get(`${API_BASE_URL}/api/consultations/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setConsultation(response.data);
      } catch (err) {
        console.error('Failed to fetch consultation:', err);
        setError('Failed to load consultation details');
      }
    };
    fetchConsultation();

    // Cleanup on unmount
    return () => {
      if (webrtcManager.current) {
        webrtcManager.current.cleanup();
      }
    };
  }, [id]);

  const handleStartCall = async () => {
    try {
      setError(null);
      const userRole = localStorage.getItem('userRole');
      const isDoctor = userRole === 'DOCTOR';

      // Initialize WebRTC
      webrtcManager.current = new WebRTCManager(
        id,
        isDoctor,
        handleRemoteStream,
        handleConnectionStateChange
      );

      const localStream = await webrtcManager.current.initialize();
      
      // Set local video
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = localStream;
      }

      setCallStarted(true);
    } catch (err) {
      console.error('Failed to start call:', err);
      setError('Failed to start video call. Please check camera/microphone permissions.');
    }
  };

  const handleRemoteStream = (stream) => {
    if (remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = stream;
    }
  };

  const handleConnectionStateChange = (state) => {
    setConnectionState(state);
    if (state === 'failed' || state === 'disconnected') {
      setError('Connection lost. Please try reconnecting.');
    }
  };

  const handleToggleVideo = () => {
    if (webrtcManager.current) {
      const newState = !videoEnabled;
      webrtcManager.current.toggleVideo(newState);
      setVideoEnabled(newState);
    }
  };

  const handleToggleAudio = () => {
    if (webrtcManager.current) {
      const newState = !audioEnabled;
      webrtcManager.current.toggleAudio(newState);
      setAudioEnabled(newState);
    }
  };

  const handleEndCall = () => {
    if (webrtcManager.current) {
      webrtcManager.current.cleanup();
    }
    navigate(`/doctor/consultations/${id}`);
  };

  const getConnectionStatusColor = () => {
    switch (connectionState) {
      case 'connected': return '#10b981';
      case 'connecting': return '#f59e0b';
      case 'failed':
      case 'disconnected': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionState) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'failed': return 'Connection Failed';
      case 'disconnected': return 'Disconnected';
      default: return 'Ready';
    }
  };

  return (
    <div style={{ 
      height: '100vh', 
      background: '#1e293b', 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{ 
        padding: '1.5rem 2rem', 
        background: '#0f172a', 
        borderBottom: '1px solid #334155',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{ 
            color: 'white', 
            fontSize: '1.5rem', 
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 700,
            marginBottom: '0.25rem'
          }}>
            Video Consultation
          </h1>
          {consultation && (
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
              {consultation.patientName} • RCH ID: {consultation.patientRchId}
            </p>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ 
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem', 
            background: getConnectionStatusColor(),
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.875rem',
            fontWeight: 600
          }}>
            {connectionState === 'connected' ? <Wifi size={16} /> : <WifiOff size={16} />}
            {getConnectionStatusText()}
          </div>
        </div>
      </div>

      {/* Video Area */}
      <div style={{ 
        flex: 1, 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '1rem',
        padding: '2rem',
        position: 'relative'
      }}>
        {/* Remote Video (Patient) */}
        <div style={{ 
          background: '#000', 
          borderRadius: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <video
            ref={remoteVideoRef}
            autoPlay
            playsInline
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: callStarted && connectionState === 'connected' ? 'block' : 'none'
            }}
          />
          {(!callStarted || connectionState !== 'connected') && (
            <div style={{ 
              position: 'absolute',
              width: '100%', 
              height: '100%', 
              background: 'linear-gradient(135deg, #475569 0%, #334155 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  width: '120px', 
                  height: '120px', 
                  borderRadius: '50%', 
                  background: '#C4622D',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem',
                  fontSize: '3rem',
                  color: 'white'
                }}>
                  {consultation?.patientName?.charAt(0) || 'P'}
                </div>
                <p style={{ color: 'white', fontSize: '1.25rem', fontWeight: 600 }}>
                  {consultation?.patientName}
                </p>
                <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
                  {callStarted ? 'Connecting...' : 'Patient'}
                </p>
              </div>
            </div>
          )}
          <div style={{ 
            position: 'absolute', 
            top: '1rem', 
            left: '1rem',
            background: 'rgba(0,0,0,0.6)',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.875rem',
            fontWeight: 600
          }}>
            Patient
          </div>
        </div>

        {/* Local Video (Doctor) */}
        <div style={{ 
          background: '#000', 
          borderRadius: '16px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transform: 'scaleX(-1)', // Mirror effect
              display: callStarted ? 'block' : 'none'
            }}
          />
          {!callStarted && (
            <div style={{ 
              position: 'absolute',
              width: '100%', 
              height: '100%', 
              background: 'linear-gradient(135deg, #475569 0%, #334155 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  width: '120px', 
                  height: '120px', 
                  borderRadius: '50%', 
                  background: '#10b981',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1rem',
                  fontSize: '3rem',
                  color: 'white'
                }}>
                  Dr
                </div>
                <p style={{ color: 'white', fontSize: '1.25rem', fontWeight: 600 }}>You</p>
                <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Doctor</p>
              </div>
            </div>
          )}
          <div style={{ 
            position: 'absolute', 
            top: '1rem', 
            left: '1rem',
            background: 'rgba(0,0,0,0.6)',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            color: 'white',
            fontSize: '0.875rem',
            fontWeight: 600
          }}>
            You (Doctor)
          </div>
          {!videoEnabled && callStarted && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              background: 'rgba(0,0,0,0.8)',
              padding: '1rem',
              borderRadius: '50%'
            }}>
              <VideoOff size={48} color="white" />
            </div>
          )}
        </div>

        {/* Start Call Button */}
        {!callStarted && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(196, 98, 45, 0.95)',
            padding: '2rem',
            borderRadius: '16px',
            maxWidth: '500px',
            textAlign: 'center',
            color: 'white',
            zIndex: 10
          }}>
            <Video size={48} style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1rem' }}>
              Ready to Start Video Consultation
            </h3>
            <p style={{ marginBottom: '1.5rem', lineHeight: 1.6 }}>
              Click below to start the video call. Make sure your camera and microphone are connected.
            </p>
            <button
              onClick={handleStartCall}
              style={{
                padding: '0.875rem 2rem',
                background: 'white',
                color: '#C4622D',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
              onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
            >
              Start Video Call
            </button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div style={{
            position: 'absolute',
            bottom: '2rem',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#ef4444',
            color: 'white',
            padding: '1rem 2rem',
            borderRadius: '8px',
            fontSize: '0.875rem',
            fontWeight: 600,
            zIndex: 10
          }}>
            {error}
          </div>
        )}
      </div>

      {/* Controls */}
      <div style={{ 
        padding: '2rem', 
        background: '#0f172a', 
        borderTop: '1px solid #334155',
        display: 'flex',
        justifyContent: 'center',
        gap: '1rem'
      }}>
        <button
          onClick={handleToggleVideo}
          disabled={!callStarted}
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: videoEnabled ? '#334155' : '#ef4444',
            border: 'none',
            color: 'white',
            cursor: callStarted ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s',
            opacity: callStarted ? 1 : 0.5
          }}
          onMouseOver={(e) => callStarted && (e.target.style.transform = 'scale(1.1)')}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
        >
          {videoEnabled ? <Video size={24} /> : <VideoOff size={24} />}
        </button>

        <button
          onClick={handleToggleAudio}
          disabled={!callStarted}
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: audioEnabled ? '#334155' : '#ef4444',
            border: 'none',
            color: 'white',
            cursor: callStarted ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s',
            opacity: callStarted ? 1 : 0.5
          }}
          onMouseOver={(e) => callStarted && (e.target.style.transform = 'scale(1.1)')}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
        >
          {audioEnabled ? <Mic size={24} /> : <MicOff size={24} />}
        </button>

        <button
          onClick={handleEndCall}
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: '#ef4444',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.target.style.transform = 'scale(1.1)'}
          onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
        >
          <PhoneOff size={24} />
        </button>
      </div>
    </div>
  );
}
