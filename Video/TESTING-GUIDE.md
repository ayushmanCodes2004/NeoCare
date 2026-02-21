# How to Test Video Call with One Camera

## The Problem
Your computer has only ONE physical camera. When one browser uses it, the other browser cannot access it.

## Solutions

### Option 1: Test with Two Devices (RECOMMENDED)
1. **Device 1 (Computer):**
   - Open http://localhost:3000
   - Enter "user1" and Join

2. **Device 2 (Phone/Tablet):**
   - Find your computer's local IP address
   - On phone, open browser and go to http://YOUR_IP:3000
   - Enter "user2" and Join
   - Start the call!

**To find your IP address on Windows:**
```
ipconfig
```
Look for "IPv4 Address" (usually starts with 192.168.x.x)

### Option 2: Use OBS Virtual Camera
1. Download OBS Studio (free)
2. Set up a virtual camera in OBS
3. One browser uses real camera, other uses OBS virtual camera

### Option 3: Test with Audio Only
Modify the app to allow audio-only calls for testing

### Option 4: Use Another Computer
- Both computers on same WiFi network
- Computer 1: http://localhost:3000
- Computer 2: http://COMPUTER1_IP:3000

## For Production Use
In real-world usage, each user will be on their own device with their own camera, so this won't be an issue!

## Quick Test Without Second Camera
You can test the signaling and connection logic by:
1. Opening two browsers
2. User1 starts call (gets camera)
3. User2 receives call (will fail to get camera, but you can see if signaling works)
4. Check browser console to see if WebRTC connection establishes
