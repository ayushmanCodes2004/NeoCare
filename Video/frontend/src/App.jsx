import React, { useState } from 'react';
import VideoCall from './components/VideoCall';
import './App.css';

function App() {
  const [userId, setUserId] = useState('');
  const [remoteUserId, setRemoteUserId] = useState('');
  const [isJoined, setIsJoined] = useState(false);

  const handleJoin = () => {
    if (userId.trim()) {
      setIsJoined(true);
    }
  };

  if (!isJoined) {
    return (
      <div className="app">
        <div className="join-container">
          <h1>WebRTC Video Call</h1>
          <input
            type="text"
            placeholder="Enter your user ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="input"
          />
          <button onClick={handleJoin} className="btn btn-primary">
            Join
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <VideoCall userId={userId} remoteUserId={remoteUserId} setRemoteUserId={setRemoteUserId} />
    </div>
  );
}

export default App;
