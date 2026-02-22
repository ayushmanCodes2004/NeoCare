# Fix: WebRTC Signaling Connection Failed

## Problem
Video call shows "Signaling connection failed" even though camera permission is granted.

## Root Cause
The frontend was using plain WebSocket, but the backend uses STOMP over WebSocket with SockJS. They weren't compatible.

## Solution

### 1. Install Required Dependencies
```bash
cd Frontend/lovable-frontend
npm install sockjs-client @stomp/stompjs
```

### 2. Use New STOMP-based WebRTC Manager
The file `Frontend/lovable-frontend/src/lib/webrtc-stomp.ts` has been created with proper STOMP support.

### 3. Update VideoCall Component
Change the import in `Frontend/lovable-frontend/src/components/VideoCall.tsx`:

```typescript
// OLD:
import { WebRTCManager } from '@/lib/webrtc';

// NEW:
import { WebRTCManager } from '@/lib/webrtc-stomp';
```

## How It Works Now

### Backend (Spring Boot)
- WebSocket endpoint: `/ws/consultation`
- Uses STOMP protocol with SockJS fallback
- Message destinations:
  - `/app/consultation/{id}/join` - Join consultation
  - `/app/consultation/{id}/signal` - Send WebRTC signals
  - `/app/consultation/{id}/leave` - Leave consultation
  - `/topic/consultation/{id}` - Receive messages

### Frontend (React)
- Connects using SockJS client
- Uses STOMP protocol for messaging
- Subscribes to consultation topic
- Sends signals through STOMP

## Steps to Fix

### Option 1: Quick Fix (Update Import)
1. Install dependencies:
```bash
cd Frontend/lovable-frontend
npm install sockjs-client @stomp/stompjs
```

2. Update `Frontend/lovable-frontend/src/components/VideoCall.tsx`:
```typescript
import { WebRTCManager } from '@/lib/webrtc-stomp';
```

3. Restart frontend:
```bash
npm run dev
```

### Option 2: Replace File
Replace the entire `webrtc.ts` file with `webrtc-stomp.ts` content.

## Testing

1. Create a high-risk visit
2. Doctor accepts consultation
3. Click "Start Video Call"
4. Should see:
   - "STOMP connected" in console
   - Camera/microphone access granted
   - Local video appears
   - Waiting for remote connection

## Troubleshooting

### Still Getting "Signaling connection failed"?

1. **Check Backend is Running:**
```bash
# Should see WebSocket configuration logs
curl http://localhost:8080/actuator/health
```

2. **Check Browser Console:**
```javascript
// Should see:
STOMP: connected
Signaling connected
```

3. **Check Network Tab:**
- Look for WebSocket connection to `/ws/consultation`
- Should show "101 Switching Protocols"

### Camera Permission Issues?

1. **Check Browser Permissions:**
   - Chrome: Settings → Privacy → Site Settings → Camera
   - Firefox: Preferences → Privacy → Permissions → Camera

2. **Use HTTPS (Production):**
   - Camera access requires HTTPS in production
   - localhost works with HTTP for development

3. **Check Console for Errors:**
```javascript
// Should NOT see:
NotAllowedError: Permission denied
NotFoundError: No camera found
```

## Backend WebSocket Configuration

The backend is already configured correctly in:
- `Backend/src/main/java/com/anc/config/WebSocketConfig.java`
- `Backend/src/main/java/com/anc/controller/WebRTCSignalingController.java`

No backend changes needed!

## Dependencies

### Frontend Package.json
Add these if not present:
```json
{
  "dependencies": {
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0"
  }
}
```

## Status
✅ STOMP-based WebRTC manager created
⏳ Pending: Install dependencies and update import
