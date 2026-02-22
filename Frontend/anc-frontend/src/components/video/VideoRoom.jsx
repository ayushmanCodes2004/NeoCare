import { useEffect, useRef, useState } from 'react';
import { WebRTCManager } from '../../utils/webrtc';
import { Video, VideoOff, Mic, MicOff, PhoneOff } from 'lucide-react';
import Button from '../ui/Button';

export default function VideoRoom({ consultationId, isDoctor, onEnd }) {
  const [localStream, setLocalStream] = useState(null);
  const [remoteStream, setRemoteStream] = useState(null);
  const [connectionState, setConnectionState] = useState('new');
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [error, setError] = useState(null);

  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const webrtcManagerRef = useRef(null);

  useEffect(() => {
    let manager = null;

    const initWebRTC = async () => {
      try {
        manager = new WebRTCManager(
          consultationId,
          isDoctor,
          (stream) => setRemoteStream(stream),
          (state) => setConnectionState(state)
        );

        const stream = await manager.initialize();
        setLocalStream(stream);
        webrtcManagerRef.current = manager;
      } catch (err) {
        console.error('WebRTC initialization failed:', err);
        setError(err.message);
      }
    };

    initWebRTC();

    return () => {
      if (manager) {
        manager.cleanup();
      }
    };
  }, [consultationId, isDoctor]);

  useEffect(() => {
    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream]);

  useEffect(() => {
    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  const toggleVideo = () => {
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.toggleVideo(!videoEnabled);
      setVideoEnabled(!videoEnabled);
    }
  };

  const toggleAudio = () => {
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.toggleAudio(!audioEnabled);
      setAudioEnabled(!audioEnabled);
    }
  };

  const handleEndCall = () => {
    if (webrtcManagerRef.current) {
      webrtcManagerRef.current.cleanup();
    }
    onEnd();
  };

  const stateColors = {
    new: 'bg-slate-500',
    connecting: 'bg-amber-500',
    connected: 'bg-teal-500',
    failed: 'bg-risk-critical',
    disconnected: 'bg-risk-critical',
  };

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <div className="flex items-center justify-between glass-card p-4">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${stateColors[connectionState]} animate-pulse`} />
          <span className="text-sm font-medium text-slate-300 capitalize">{connectionState}</span>
        </div>
        {error && (
          <span className="text-xs text-risk-critical">{error}</span>
        )}
      </div>

      {/* Video Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Remote Video */}
        <div className="relative aspect-video bg-navy-900 rounded-2xl overflow-hidden">
          <video
            ref={remoteVideoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
          />
          {!remoteStream && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <VideoOff size={48} className="mx-auto mb-2 text-slate-600" />
                <p className="text-sm text-slate-500">Waiting for remote video...</p>
              </div>
            </div>
          )}
          <div className="absolute bottom-4 left-4 px-3 py-1 rounded-lg bg-black/50 backdrop-blur text-xs text-white">
            {isDoctor ? 'Worker' : 'Doctor'}
          </div>
        </div>

        {/* Local Video */}
        <div className="relative aspect-video bg-navy-900 rounded-2xl overflow-hidden">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover scale-x-[-1]"
          />
          {!videoEnabled && (
            <div className="absolute inset-0 flex items-center justify-center bg-navy-900">
              <VideoOff size={48} className="text-slate-600" />
            </div>
          )}
          <div className="absolute bottom-4 left-4 px-3 py-1 rounded-lg bg-black/50 backdrop-blur text-xs text-white">
            You
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-3">
        <Button
          variant={videoEnabled ? 'secondary' : 'danger'}
          onClick={toggleVideo}
          className="w-12 h-12 rounded-full p-0"
        >
          {videoEnabled ? <Video size={20} /> : <VideoOff size={20} />}
        </Button>
        <Button
          variant={audioEnabled ? 'secondary' : 'danger'}
          onClick={toggleAudio}
          className="w-12 h-12 rounded-full p-0"
        >
          {audioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
        </Button>
        <Button
          variant="danger"
          onClick={handleEndCall}
          className="w-12 h-12 rounded-full p-0"
        >
          <PhoneOff size={20} />
        </Button>
      </div>
    </div>
  );
}
