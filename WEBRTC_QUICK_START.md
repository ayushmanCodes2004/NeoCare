# WebRTC Video Consultation - Quick Start Guide

## 🚀 What Was Implemented

Complete peer-to-peer video consultation system using WebRTC with STOMP WebSocket signaling.

## 📦 Installation

### Backend (Spring Boot)
```bash
cd Backend
mvn clean install
mvn spring-boot:run
```

The WebSocket dependency is already added to `pom.xml`.

### Frontend (React)
```bash
cd Frontend/anc-frontend
npm install sockjs-client @stomp/stompjs
npm run dev
```

## 🎥 How to Test

### Option 1: Two Browser Windows (Same Computer)

1. **Start Backend**: `mvn spring-boot:run` (port 8080)
2. **Start Frontend**: `npm run dev` (port 5173)
3. **Window 1 - Doctor**:
   - Go to `http://localhost:5173/doctor/login`
   - Login with doctor credentials
   - Navigate to a SCHEDULED consultation
   - Click "Start Video Call"
   - Grant camera/microphone permissions
   - Click "Start Video Call" button

4. **Window 2 - Patient** (simulated):
   - Open same consultation URL in new window
   - Grant permissions
   - Videos should connect automatically

### Option 2: Two Different Computers (Same Network)

1. **Computer 1 (Backend + Doctor)**:
   - Run backend: `mvn spring-boot:run`
   - Run frontend: `npm run dev`
   - Login as doctor and start call

2. **Computer 2 (Patient)**:
   - Open `http://<computer1-ip>:5173`
   - Login and join consultation

## ✅ What to Expect

When working correctly:
- ✅ Local video appears (mirrored)
- ✅ Remote video appears
- ✅ Connection status shows "Connected" (green badge)
- ✅ Video toggle button works
- ✅ Audio toggle button works
- ✅ End call button works

## 🔧 Key Files

### Frontend
- `Frontend/anc-frontend/src/utils/webrtc.js` - WebRTC manager
- `Frontend/anc-frontend/src/pages/VideoConsultationPage.jsx` - Video UI
- `Frontend/anc-frontend/WEBRTC_SETUP.md` - Setup instructions

### Backend
- `Backend/src/main/java/com/anc/config/WebSocketConfig.java` - WebSocket config
- `Backend/src/main/java/com/anc/controller/WebRTCSignalingController.java` - Signaling
- `Backend/pom.xml` - Dependencies (spring-boot-starter-websocket)

## 🌐 Architecture

```
┌─────────┐                    ┌─────────┐
│ Doctor  │                    │ Patient │
│ Browser │                    │ Browser │
└────┬────┘                    └────┬────┘
     │                              │
     │  ┌────────────────────────┐  │
     ├──┤  WebRTC P2P Video     ├──┤  (Direct)
     │  └────────────────────────┘  │
     │                              │
     │  ┌────────────────────────┐  │
     └──┤  STOMP WebSocket       ├──┘
        │  Signaling Server      │
        │  (Spring Boot)         │
        └────────────────────────┘
```

### Flow
1. Both users connect to WebSocket signaling server
2. Doctor creates WebRTC offer
3. Patient receives offer and creates answer
4. ICE candidates exchanged for NAT traversal
5. Peer-to-peer video/audio connection established
6. Media flows directly between browsers (not through server)

## 🐛 Common Issues

### "Failed to start video call"
**Problem**: Camera/microphone permission denied  
**Solution**: Grant permissions in browser settings

### "Connection Failed"
**Problem**: Backend not running  
**Solution**: Start backend with `mvn spring-boot:run`

### "No remote video"
**Problem**: Firewall or NAT issues  
**Solution**: 
- Test on same network first
- Check browser console for errors
- For production, add TURN server

### "Module not found: sockjs-client"
**Problem**: Dependencies not installed  
**Solution**: Run `npm install sockjs-client @stomp/stompjs`

## 📱 Browser Requirements

- Chrome 90+ (recommended)
- Firefox 88+
- Edge 90+
- Safari 14+

Must support:
- WebRTC
- getUserMedia API
- WebSocket

## 🔒 Security Notes

### Current (Development)
- WebSocket endpoint is open
- No authentication on signaling
- Suitable for testing only

### Production Requirements
- Add JWT authentication to WebSocket
- Enable HTTPS/WSS
- Add TURN server for restrictive networks
- Validate consultation access

## 📊 Performance

### Default Settings
- Video: 1280x720 @ 30fps
- Audio: Echo cancellation, noise suppression enabled
- STUN servers: Google public STUN

### Bandwidth Usage
- ~1-2 Mbps per direction for 720p video
- ~50-100 Kbps for audio

## 🎯 Next Steps

1. **Test locally** with two browser windows
2. **Test on network** with two computers
3. **Add TURN server** for production (optional)
4. **Enable HTTPS** for production deployment
5. **Add authentication** to WebSocket endpoint
6. **Monitor quality** and adjust settings

## 📚 Documentation

- `WEBRTC_IMPLEMENTATION_COMPLETE.md` - Full technical documentation
- `Frontend/anc-frontend/WEBRTC_SETUP.md` - Frontend setup guide
- `DOCTOR_MODULE_FRONTEND_COMPLETE.md` - Doctor module overview

## 💡 Tips

1. **Use Chrome** for best WebRTC support
2. **Test locally first** before network testing
3. **Check console** for detailed error messages
4. **Grant permissions** when prompted
5. **Use headphones** to prevent echo feedback

## ✨ Features

- ✅ Real-time video streaming
- ✅ Real-time audio streaming
- ✅ Video on/off toggle
- ✅ Audio mute/unmute
- ✅ Connection status indicator
- ✅ Automatic reconnection
- ✅ Graceful cleanup
- ✅ Error handling
- ✅ Responsive UI

## 🎉 Success!

If you see both video streams and the connection status shows "Connected", congratulations! Your WebRTC video consultation is working.

For production deployment, see `WEBRTC_IMPLEMENTATION_COMPLETE.md` for security and optimization recommendations.
