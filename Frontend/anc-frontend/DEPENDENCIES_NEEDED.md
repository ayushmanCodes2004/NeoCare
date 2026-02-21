# Required Dependencies for WebRTC

## Install Command

```bash
npm install sockjs-client @stomp/stompjs
```

## Package Versions

```json
{
  "dependencies": {
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0"
  }
}
```

## What These Do

### sockjs-client
- Provides WebSocket fallback support
- Ensures compatibility across browsers
- Handles connection reliability
- Used by Spring Boot's SockJS support

### @stomp/stompjs
- STOMP protocol implementation
- Message broker client
- Pub/sub messaging over WebSocket
- Used for WebRTC signaling

## Verification

After installation, verify in your `package.json`:

```bash
cat package.json | grep -A 2 "sockjs-client"
```

Should show:
```json
"sockjs-client": "^1.6.1",
"@stomp/stompjs": "^7.0.0",
```

## Usage in Code

These are imported in `src/utils/webrtc.js`:

```javascript
import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';
```

## Troubleshooting

### If installation fails:
```bash
# Clear cache and retry
npm cache clean --force
npm install sockjs-client @stomp/stompjs
```

### If import errors occur:
```bash
# Reinstall all dependencies
rm -rf node_modules package-lock.json
npm install
```

### If TypeScript errors:
```bash
# Install type definitions (if using TypeScript)
npm install --save-dev @types/sockjs-client
```

## Alternative: Add to package.json manually

Edit `package.json` and add to dependencies:
```json
{
  "dependencies": {
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0"
  }
}
```

Then run:
```bash
npm install
```

## Complete Dependencies List

Your `package.json` should include (at minimum):

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "react-hook-form": "^7.48.2",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0",
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0"
  }
}
```

## Next Steps

After installing:
1. Restart development server: `npm run dev`
2. Check browser console for errors
3. Test video consultation feature
4. Verify WebSocket connection in Network tab

## Documentation

- See `WEBRTC_SETUP.md` for complete setup guide
- See `WEBRTC_QUICK_START.md` for testing instructions
- See `WEBRTC_IMPLEMENTATION_COMPLETE.md` for technical details
