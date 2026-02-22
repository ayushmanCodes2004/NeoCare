# Test WebRTC Connection

## Quick Test Steps

### 1. Restart Frontend
```bash
cd Frontend/lovable-frontend
npm run dev
```

### 2. Open Browser Console
Press F12 to open Developer Tools

### 3. Navigate to Video Call
1. Login as worker
2. Go to patient with high-risk visit
3. Click on consultation
4. Click "Start Video Call"

### 4. Check Console Messages

#### ✅ Success - Should See:
```
STOMP: Opening Web Socket...
STOMP: Web Socket Opened...
STOMP: connected to server
Signaling connected
Connection state: new
Connection state: connecting
```

#### ❌ Old Error (Fixed):
```
WebSocket error: [object Event]
Signaling connection failed
```

### 5. Check Network Tab
1. Go to Network tab in DevTools
2. Filter by "WS" (WebSocket)
3. Should see connection to `/ws/consultation`
4. Status should be "101 Switching Protocols"
5. Messages tab should show STOMP frames

## What to Look For

### STOMP Connection
```
>>> CONNECT
accept-version:1.0,1.1,1.2
heart-beat:4000,4000

<<< CONNECTED
version:1.2
heart-beat:4000,4000
```

### Join Message
```
>>> SEND
destination:/app/consultation/{id}/join
content-type:application/json

{"role":"worker","consultationId":"..."}
```

### Subscription
```
>>> SUBSCRIBE
id:sub-0
destination:/topic/consultation/{id}
```

## Common Issues

### Issue 1: "Module not found: @/lib/webrtc-stomp"
**Solution:** Restart the dev server
```bash
# Stop with Ctrl+C
npm run dev
```

### Issue 2: "Cannot find module 'sockjs-client'"
**Solution:** Dependencies not installed
```bash
npm install sockjs-client @stomp/stompjs
```

### Issue 3: Still seeing "Signaling connection failed"
**Solution:** Clear browser cache and hard reload
- Chrome: Ctrl+Shift+R
- Firefox: Ctrl+F5

### Issue 4: Backend not responding
**Solution:** Check backend is running
```bash
curl http://localhost:8080/actuator/health
```

## Success Criteria

✅ Console shows "STOMP: connected"
✅ Console shows "Signaling connected"
✅ Network tab shows WebSocket connection
✅ No "Signaling connection failed" error
✅ Camera permission prompt appears
✅ Local video stream appears

## If Still Not Working

1. **Check all services running:**
   - Backend: http://localhost:8080
   - Frontend: http://localhost:5173
   - RAG Pipeline: http://localhost:8000

2. **Check browser console for errors**

3. **Check Network tab for failed requests**

4. **Try different browser (Chrome recommended)**

5. **Check firewall/antivirus not blocking WebSocket**

## Expected Timeline

- Connection: < 2 seconds
- Camera access: < 1 second (after permission)
- Video appears: < 1 second
- Total: < 5 seconds from click to video

## Debug Commands

### Check WebSocket in Browser Console
```javascript
// Should show WebSocket connection
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('ws://'))
```

### Check STOMP Client State
```javascript
// In VideoCall component, add:
console.log('STOMP state:', stompClient?.connected);
```

### Check Media Devices
```javascript
// Check available cameras
navigator.mediaDevices.enumerateDevices()
  .then(devices => console.log(devices.filter(d => d.kind === 'videoinput')));
```
