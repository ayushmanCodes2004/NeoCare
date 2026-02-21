# WebRTC Setup Instructions

## Quick Start

### 1. Install Required Dependencies

```bash
npm install sockjs-client @stomp/stompjs
```

### 2. Verify Installation

Check that these packages are in your `package.json`:
```json
{
  "dependencies": {
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0"
  }
}
```

### 3. Environment Configuration (Optional)

Create `.env` file in `Frontend/anc-frontend/`:
```
VITE_API_BASE_URL=http://localhost:8080
```

### 4. Start Development Server

```bash
npm run dev
```

## Testing Video Consultation

### Prerequisites
- Backend running on `http://localhost:8080`
- Camera and microphone connected
- Two browser windows (or different browsers)

### Test Steps

1. **Window 1 - Doctor**:
   - Navigate to `http://localhost:5173/doctor/login`
   - Login as doctor
   - Go to consultations
   - Click on a SCHEDULED consultation
   - Click "Start Video Call"
   - Grant camera/microphone permissions
   - Click "Start Video Call" button

2. **Window 2 - Patient** (simulated):
   - Open same consultation URL
   - Grant camera/microphone permissions
   - Video should connect automatically

3. **Verify**:
   - Both videos should appear
   - Connection status should show "Connected" (green)
   - Video/audio toggles should work
   - End call should work

## Troubleshooting

### "Module not found: sockjs-client"
```bash
npm install sockjs-client @stomp/stompjs
```

### "WebSocket connection failed"
- Verify backend is running: `http://localhost:8080`
- Check browser console for errors
- Ensure WebSocket endpoint is accessible

### "Camera permission denied"
- Grant permissions in browser settings
- Try different browser (Chrome recommended)
- Check if camera is being used by another app

### "No remote video"
- Check browser console for WebRTC errors
- Verify both users are in same consultation
- Check network connectivity
- Try refreshing both windows

## Browser Compatibility

### Recommended
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

### Required Features
- WebRTC support
- getUserMedia API
- WebSocket support
- STOMP over WebSocket

## Production Deployment

### Build for Production
```bash
npm run build
```

### Environment Variables
```
VITE_API_BASE_URL=https://your-production-api.com
```

### HTTPS Required
WebRTC requires HTTPS in production. Ensure your deployment uses:
- HTTPS for frontend
- WSS (WebSocket Secure) for signaling

## Additional Resources

- See `WEBRTC_IMPLEMENTATION_COMPLETE.md` for full documentation
- Check `src/utils/webrtc.js` for WebRTC implementation
- Review `src/pages/VideoConsultationPage.jsx` for UI implementation
