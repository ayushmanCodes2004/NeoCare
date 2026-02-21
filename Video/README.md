# WebRTC Video Call Application

One-on-one video calling application with audio and video using WebRTC, React, and Spring Boot.

## Architecture

- **Frontend**: React with Vite
- **Backend**: Spring Boot with WebSocket (STOMP)
- **Protocol**: WebRTC for peer-to-peer media streaming
- **Signaling**: WebSocket for exchanging connection info

## Setup Instructions

### Backend (Spring Boot)

1. Navigate to backend directory:
```bash
cd backend
```

2. Run the application:
```bash
mvn spring-boot:run
```

Server will start on `http://localhost:8080`

### Frontend (React)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Application will open on `http://localhost:3000`

## How to Use

1. Open the application in two different browser windows/tabs
2. Enter a unique user ID in each window (e.g., "user1" and "user2")
3. Click "Join" in both windows
4. In one window, enter the other user's ID and click "Start Call"
5. The call will connect and you'll see both video streams
6. Use controls to mute/unmute audio, toggle video, or end the call

## Features

- Real-time video and audio streaming
- Mute/unmute audio
- Enable/disable video
- Clean, responsive UI
- Peer-to-peer connection via WebRTC
- WebSocket signaling server

## Tech Stack

- React 18
- Vite
- WebRTC API
- SockJS + STOMP
- Spring Boot 3.2
- Spring WebSocket
- Maven
