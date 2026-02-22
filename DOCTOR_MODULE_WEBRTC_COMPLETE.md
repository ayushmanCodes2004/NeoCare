# Doctor Module with WebRTC - Implementation Complete ✅

## Overview

The doctor module now uses **WebRTC peer-to-peer video calls** instead of Daily.co. This eliminates the need for external video services and API keys, providing a completely self-hosted solution.

## ✅ What Changed

### 1. Removed Daily.co Dependencies
- ❌ Removed `spring-boot-starter-webflux` from pom.xml
- ❌ Removed Daily.co configuration from application.yml
- ❌ Removed VideoSessionService dependency from ConsultationService

### 2. Updated ConsultationService
- ✅ `startCall()` method now uses WebRTC signaling
- ✅ Sets `roomUrl` to `"webrtc://{consultationId}"` as a marker
- ✅ No tokens needed (peer-to-peer connection)
- ✅ Signaling happens via STOMP WebSocket at `/ws/consultation`

### 3. Existing WebRTC Infrastructure (Already in Place)
- ✅ `WebSocketConfig.java` - STOMP WebSocket configuration
- ✅ `WebRTCSignalingController.java` - Signaling server
- ✅ `Frontend/anc-frontend/src/utils/webrtc.js` - WebRTC manager

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WEBRTC VIDEO CONSULTATION                        │
└─────────────────────────────────────────────────────────────────────┘

Doctor Browser                    Spring Boot Server              Worker Browser
     │                                   │                              │
     │  1. Start Call                    │                              │
     ├──────────────────────────────────>│                              │
     │  POST /api/consultations/{id}/    │                              │
     │       start-call                  │                              │
     │                                   │                              │
     │  2. Connect WebSocket             │                              │
     ├──────────────────────────────────>│                              │
     │  ws://localhost:8080/ws/          │                              │
     │     consultation (SockJS)         │                              │
     │                                   │                              │
     │  3. Subscribe to topic            │                              │
     ├──────────────────────────────────>│                              │
     │  /topic/consultation/{id}         │                              │
     │                                   │                              │
     │  4. Send JOIN message             │                              │
     ├──────────────────────────────────>│                              │
     │  {"role": "doctor"}               │                              │
     │                                   │                              │
     │                                   │  5. Worker connects          │
     │                                   │<─────────────────────────────┤
     │                                   │  ws://localhost:8080/ws/     │
     │                                   │     consultation             │
     │                                   │                              │
     │                                   │  6. Worker subscribes        │
     │                                   │<─────────────────────────────┤
     │                                   │  /topic/consultation/{id}    │
     │                                   │                              │
     │                                   │  7. Worker sends JOIN        │
     │                                   │<─────────────────────────────┤
     │                                   │  {"role": "worker"}          │
     │                                   │                              │
     │  8. Receive user-joined           │                              │
     │<──────────────────────────────────┤                              │
     │  notification                     │                              │
     │                                   │                              │
     │  9. Create WebRTC Offer           │                              │
     │  (SDP with media capabilities)    │                              │
     │                                   │                              │
     │  10. Send OFFER via STOMP         │                              │
     ├──────────────────────────────────>│                              │
     │  {"type": "offer", "offer": ...}  │                              │
     │                                   │                              │
     │                                   │  11. Forward OFFER           │
     │                                   ├─────────────────────────────>│
     │                                   │                              │
     │                                   │  12. Worker creates ANSWER   │
     │                                   │                              │
     │                                   │  13. Send ANSWER via STOMP   │
     │                                   │<─────────────────────────────┤
     │                                   │  {"type": "answer", ...}     │
     │                                   │                              │
     │  14. Receive ANSWER               │                              │
     │<──────────────────────────────────┤                              │
     │                                   │                              │
     │  15. Exchange ICE candidates      │                              │
     │<─────────────────────────────────>│<────────────────────────────>│
     │  (NAT traversal information)      │                              │
     │                                   │                              │
     │  16. PEER-TO-PEER CONNECTION ESTABLISHED                         │
     │<═════════════════════════════════════════════════════════════════>│
     │                                   │                              │
     │  Video/Audio streams flow directly between browsers              │
     │  (no media goes through server)   │                              │
     │                                   │                              │
```

## 🔧 How It Works

### 1. Consultation Flow

```
Doctor accepts consultation
       ↓
Doctor clicks "Start Call"
       ↓
POST /api/consultations/{id}/start-call
       ↓
Status: ACCEPTED → IN_PROGRESS
roomUrl: "webrtc://{consultationId}"
       ↓
Doctor's browser:
  - Requests camera/microphone
  - Creates RTCPeerConnection
  - Connects to ws://localhost:8080/ws/consultation
  - Subscribes to /topic/consultation/{id}
  - Sends JOIN message
       ↓
Worker's browser:
  - Receives notification
  - Requests camera/microphone
  - Creates RTCPeerConnection
  - Connects to ws://localhost:8080/ws/consultation
  - Subscribes to /topic/consultation/{id}
  - Sends JOIN message
       ↓
Doctor receives "user-joined" notification
       ↓
Doctor creates WebRTC OFFER
       ↓
OFFER sent via STOMP → forwarded to Worker
       ↓
Worker creates WebRTC ANSWER
       ↓
ANSWER sent via STOMP → forwarded to Doctor
       ↓
Both exchange ICE candidates via STOMP
       ↓
Peer-to-peer connection established
       ↓
Video/audio streams flow directly
```

### 2. WebRTC Signaling Messages

#### Join Message
```json
{
  "role": "doctor",
  "consultationId": "uuid"
}
```

#### Offer Message (Doctor → Worker)
```json
{
  "type": "offer",
  "offer": {
    "type": "offer",
    "sdp": "v=0\r\no=- 123456789 2 IN IP4 127.0.0.1\r\n..."
  }
}
```

#### Answer Message (Worker → Doctor)
```json
{
  "type": "answer",
  "answer": {
    "type": "answer",
    "sdp": "v=0\r\no=- 987654321 2 IN IP4 127.0.0.1\r\n..."
  }
}
```

#### ICE Candidate Message (Both directions)
```json
{
  "type": "ice-candidate",
  "candidate": {
    "candidate": "candidate:1 1 UDP 2130706431 192.168.1.100 54321 typ host",
    "sdpMLineIndex": 0,
    "sdpMid": "0"
  }
}
```

## 📁 File Structure

### Backend Files
```
Backend/
├── src/main/java/com/anc/
│   ├── config/
│   │   └── WebSocketConfig.java              ✅ STOMP WebSocket config
│   ├── controller/
│   │   ├── ConsultationController.java       ✅ Updated (no changes needed)
│   │   └── WebRTCSignalingController.java    ✅ Signaling server
│   ├── service/
│   │   └── ConsultationService.java          ✅ Updated (WebRTC mode)
│   └── entity/
│       └── ConsultationEntity.java           ✅ roomUrl stores "webrtc://{id}"
└── src/main/resources/
    └── application.yml                        ✅ No Daily.co config needed
```

### Frontend Files
```
Frontend/anc-frontend/src/
├── utils/
│   └── webrtc.js                             ✅ WebRTC manager
├── pages/
│   └── VideoConsultationPage.jsx             ✅ Video call UI
└── api/
    └── consultationApi.js                     ✅ API calls
```

## 🚀 Setup Instructions

### Backend Setup

1. **Verify dependencies** (already in pom.xml):
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-websocket</artifactId>
</dependency>
```

2. **Build and run**:
```bash
cd Backend
mvn clean install
mvn spring-boot:run
```

WebSocket endpoint: `ws://localhost:8080/ws/consultation`

### Frontend Setup

1. **Install WebRTC dependencies**:
```bash
cd Frontend/anc-frontend
npm install sockjs-client @stomp/stompjs
```

2. **Run development server**:
```bash
npm run dev
```

## 🧪 Testing

### Test Flow

1. **Create doctor account**:
```bash
curl -X POST http://localhost:8080/api/doctor/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Dr. Priya Sharma",
    "phone": "9988776655",
    "email": "priya@hospital.in",
    "password": "SecurePass123",
    "specialization": "Obstetrics & Gynaecology",
    "hospital": "District Hospital",
    "district": "Bangalore Rural",
    "registrationNo": "KA-12345"
  }'
```

2. **Doctor login**:
```bash
curl -X POST http://localhost:8080/api/doctor/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9988776655",
    "password": "SecurePass123"
  }'
```

3. **Create high-risk visit** (as ANC worker) - auto-creates consultation

4. **Doctor views priority queue**:
```bash
curl -X GET http://localhost:8080/api/consultations/queue \
  -H "Authorization: Bearer <doctor-jwt-token>"
```

5. **Doctor accepts consultation**:
```bash
curl -X POST http://localhost:8080/api/consultations/{id}/accept \
  -H "Authorization: Bearer <doctor-jwt-token>"
```

6. **Doctor starts video call**:
```bash
curl -X POST http://localhost:8080/api/consultations/{id}/start-call \
  -H "Authorization: Bearer <doctor-jwt-token>"
```

Response:
```json
{
  "consultationId": "uuid",
  "status": "IN_PROGRESS",
  "roomUrl": "webrtc://uuid",
  "doctorToken": null,
  "workerToken": null,
  ...
}
```

7. **Open video call in browser**:
   - Doctor: Navigate to `/consultations/{id}/video`
   - Worker: Navigate to `/consultations/{id}/video`
   - Both grant camera/microphone permissions
   - Video streams appear automatically

## 🎯 Key Differences from Daily.co

| Feature | Daily.co | WebRTC (Current) |
|---------|----------|------------------|
| **External Service** | Required | Not needed |
| **API Key** | Required | Not needed |
| **Cost** | Free tier limited | Completely free |
| **Room URL** | `https://domain.daily.co/room` | `webrtc://{consultationId}` |
| **Tokens** | Generated per user | Not needed |
| **Signaling** | Daily.co servers | Your Spring Boot server |
| **Media Routing** | Peer-to-peer (same) | Peer-to-peer |
| **STUN Servers** | Daily.co provided | Google public STUN |
| **TURN Servers** | Daily.co provided | Need to add if required |
| **Setup Complexity** | Medium | Low |
| **Control** | Limited | Full control |

## 🔒 Security Considerations

### Current Implementation
- WebSocket endpoint is open (suitable for development)
- Peer-to-peer media (encrypted by default with DTLS-SRTP)

### Production Recommendations

1. **Add WebSocket Authentication**:
```java
@Override
public void configureClientInboundChannel(ChannelRegistration registration) {
    registration.interceptors(new ChannelInterceptor() {
        @Override
        public Message<?> preSend(Message<?> message, MessageChannel channel) {
            StompHeaderAccessor accessor = 
                MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);
            
            if (StompCommand.CONNECT.equals(accessor.getCommand())) {
                String token = accessor.getFirstNativeHeader("Authorization");
                // Validate JWT token
                // Set user principal
            }
            return message;
        }
    });
}
```

2. **Validate Consultation Access**:
   - Check if user is authorized for consultation
   - Verify doctor/patient relationship

3. **Add TURN Server** (for restrictive networks):
```javascript
const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    {
      urls: 'turn:your-turn-server.com:3478',
      username: 'username',
      credential: 'password'
    }
  ]
};
```

4. **Enable HTTPS/WSS**:
   - WebRTC requires HTTPS in production
   - Use WSS (WebSocket Secure)

## 🐛 Troubleshooting

### "Failed to start video call"
- **Cause**: Camera/microphone permission denied
- **Solution**: Grant permissions in browser settings

### "Connection Failed"
- **Cause**: WebSocket server not running
- **Solution**: Verify backend is running on port 8080

### "No remote video"
- **Cause**: ICE candidates not exchanged or NAT issues
- **Solution**: 
  - Check browser console for errors
  - Verify STUN servers are reachable
  - Add TURN server for restrictive networks

### "WebSocket connection failed"
- **Cause**: CORS or WebSocket configuration issue
- **Solution**: 
  - Verify `setAllowedOriginPatterns("*")` in WebSocketConfig
  - Check browser console for CORS errors

## 📊 Advantages of WebRTC

### ✅ Pros
- **No external dependencies** - completely self-hosted
- **No API keys** - no signup or configuration needed
- **No cost** - unlimited usage
- **Full control** - customize everything
- **Privacy** - media never goes through external servers
- **Low latency** - direct peer-to-peer connection
- **Encrypted** - DTLS-SRTP encryption by default

### ⚠️ Cons
- **NAT traversal** - may need TURN server for restrictive networks
- **Scaling** - need to handle signaling server load
- **Monitoring** - need to implement your own analytics
- **Fallback** - need to handle connection failures

## 🎓 WebRTC Concepts

### STUN (Session Traversal Utilities for NAT)
- Helps peers discover their public IP addresses
- Used for NAT traversal
- Free public servers available (Google, etc.)

### TURN (Traversal Using Relays around NAT)
- Relay server for restrictive networks
- Used when direct peer-to-peer fails
- Requires setup (coturn, etc.)

### ICE (Interactive Connectivity Establishment)
- Framework for finding best connection path
- Tries multiple candidates (host, srflx, relay)
- Automatically selects optimal route

### SDP (Session Description Protocol)
- Describes media capabilities
- Exchanged in offer/answer
- Contains codecs, formats, etc.

## 📝 API Endpoints

### REST Endpoints
- `POST /api/consultations/{id}/start-call` - Start WebRTC call
- `GET /api/consultations/{id}` - Get consultation details
- `POST /api/consultations/{id}/complete` - Complete consultation

### WebSocket Endpoints
- **Connect**: `ws://localhost:8080/ws/consultation` (SockJS)
- **Subscribe**: `/topic/consultation/{consultationId}`
- **Send Signal**: `/app/consultation/{consultationId}/signal`
- **Join**: `/app/consultation/{consultationId}/join`
- **Leave**: `/app/consultation/{consultationId}/leave`

## ✨ Summary

The doctor module now uses **WebRTC for peer-to-peer video calls**:

- ✅ No external video service needed
- ✅ No API keys required
- ✅ Completely free and self-hosted
- ✅ Full control over signaling and media
- ✅ STOMP WebSocket signaling server
- ✅ Existing WebRTC infrastructure reused
- ✅ ConsultationService updated for WebRTC mode
- ✅ No compilation errors
- ✅ Ready to test

**Next Steps**:
1. Run database migration
2. Test doctor signup/login
3. Create high-risk visit
4. Test video call with WebRTC

---

**Implementation Status**: Complete ✅
**Video Technology**: WebRTC (peer-to-peer)
**External Dependencies**: None
**Cost**: Free
