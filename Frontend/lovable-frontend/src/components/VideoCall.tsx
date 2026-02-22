import { useEffect, useRef, useState } from 'react';
import { WebRTCManager } from '@/lib/webrtc-stomp';
import { Video, VideoOff, Mic, MicOff, PhoneOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface VideoCallProps {
  consultationId: string;
  isDoctor: boolean;
  onEnd: () => void;
}

export default function VideoCall({ consultationId, isDoctor, onEnd }: VideoCallProps) {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [connectionState, setConnectionState] = useState('new');
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const webrtcManagerRef = useRef<WebRTCManager | null>(null);

  useEffect(() => {
    let manager: WebRTCManager | null = null;

    const initWebRTC = async () => {
      try {
        setLoading(true);
        manager = new WebRTCManager(
          consultationId,
          isDoctor,
          (stream) => setRemoteStream(stream),
          (state) => setConnectionState(state)
        );

        const stream = await manager.initialize();
        setLocalStream(stream);
        webrtcManagerRef.current = manager;
        setLoading(false);
      } catch (err: any) {
        console.error('WebRTC initialization failed:', err);
        setError(err.message || 'Failed to access camera/microphone');
        setLoading(false);
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

  const stateColors: Record<string, string> = {
    new: 'bg-muted-foreground',
    connecting: 'bg-warning',
    connected: 'bg-success',
    failed: 'bg-destructive',
    disconnected: 'bg-destructive',
  };

  const stateLabels: Record<string, string> = {
    new: 'Initializing',
    connecting: 'Connecting',
    connected: 'Connected',
    failed: 'Connection Failed',
    disconnected: 'Disconnected',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Initializing video call...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center max-w-md">
          <VideoOff className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Camera Access Required</h3>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <p className="text-xs text-muted-foreground">
            Please allow camera and microphone access in your browser settings and refresh the page.
          </p>
          <Button onClick={onEnd} variant="outline" className="mt-4">
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <div className="flex items-center justify-between bg-card rounded-lg border p-4">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${stateColors[connectionState]} animate-pulse`} />
          <span className="text-sm font-medium text-foreground">{stateLabels[connectionState]}</span>
        </div>
        <span className="text-xs text-muted-foreground">
          Consultation ID: {consultationId.slice(0, 8)}
        </span>
      </div>

      {/* Video Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Remote Video (Larger on mobile) */}
        <div className="relative aspect-video bg-muted rounded-lg overflow-hidden order-1">
          <video
            ref={remoteVideoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
          />
          {!remoteStream && (
            <div className="absolute inset-0 flex items-center justify-center bg-muted">
              <div className="text-center">
                <VideoOff size={48} className="mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Waiting for {isDoctor ? 'worker' : 'doctor'}...</p>
              </div>
            </div>
          )}
          <div className="absolute bottom-4 left-4 px-3 py-1 rounded-lg bg-black/70 backdrop-blur text-xs text-white font-medium">
            {isDoctor ? 'Worker' : 'Doctor'}
          </div>
        </div>

        {/* Local Video */}
        <div className="relative aspect-video bg-muted rounded-lg overflow-hidden order-2">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover scale-x-[-1]"
          />
          {!videoEnabled && (
            <div className="absolute inset-0 flex items-center justify-center bg-muted">
              <VideoOff size={48} className="text-muted-foreground" />
            </div>
          )}
          <div className="absolute bottom-4 left-4 px-3 py-1 rounded-lg bg-black/70 backdrop-blur text-xs text-white font-medium">
            You
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-3 py-4">
        <Button
          variant={videoEnabled ? 'secondary' : 'destructive'}
          onClick={toggleVideo}
          size="icon"
          className="h-14 w-14 rounded-full"
        >
          {videoEnabled ? <Video size={24} /> : <VideoOff size={24} />}
        </Button>
        <Button
          variant={audioEnabled ? 'secondary' : 'destructive'}
          onClick={toggleAudio}
          size="icon"
          className="h-14 w-14 rounded-full"
        >
          {audioEnabled ? <Mic size={24} /> : <MicOff size={24} />}
        </Button>
        <Button
          variant="destructive"
          onClick={handleEndCall}
          size="icon"
          className="h-14 w-14 rounded-full"
        >
          <PhoneOff size={24} />
        </Button>
      </div>

      {/* Instructions */}
      <div className="bg-muted/50 rounded-lg p-4 text-center">
        <p className="text-xs text-muted-foreground">
          Click the video or microphone buttons to toggle them. Click the phone button to end the call.
        </p>
      </div>
    </div>
  );
}
