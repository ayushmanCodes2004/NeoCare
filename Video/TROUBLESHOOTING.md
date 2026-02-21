# Camera Access Troubleshooting

## If you get "Device in use" error:

### Option 1: Close everything and restart
1. Close ALL Chrome windows
2. Close ALL Edge windows  
3. Open Task Manager (Ctrl+Shift+Esc)
4. End any remaining chrome.exe or msedge.exe processes
5. Restart browsers fresh

### Option 2: Check Windows Camera Settings
1. Press Windows + I (Settings)
2. Go to Privacy & Security > Camera
3. Make sure "Let apps access your camera" is ON
4. Check which apps recently accessed camera
5. Close those apps

### Option 3: Use different approach
Instead of two browsers on same machine, you can:
- Use your phone's browser + desktop browser
- Use two different computers on same network
- Use incognito/private windows in different browsers

### Option 4: Test with one user first
1. Open just ONE browser
2. Join as "user1"
3. Start call to "user2" (even though user2 isn't there)
4. Check if YOUR camera works
5. If yes, then open second browser for user2

## Common Issues:

**Camera permission denied:**
- Click the camera icon in browser address bar
- Allow camera and microphone access
- Refresh the page

**No video showing:**
- Check browser console (F12) for errors
- Make sure you clicked "Allow" for camera permissions
- Try a different browser

**Connection not establishing:**
- Make sure backend is running on port 8080
- Check browser console for WebSocket errors
- Verify both users entered correct IDs
