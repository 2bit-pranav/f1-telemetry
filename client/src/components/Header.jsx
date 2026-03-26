import React from 'react';

// Accept the new 'track' and 'lap' props here
function Header({ track, lap, isConnected }) {
  return (
    <div className="header">
      <div className="race-info">
        {/* Use the variables instead of the hardcoded text */}
        <h1>{track}</h1>
        <p>{lap}</p>
      </div>
      
      <div className="connection-status">
        <span className="status-indicator" style={{ color: isConnected ? '#00ff00' : '#ff0000' }}>
          {isConnected ? '🟢 Live' : '🔴 Disconnected'}
        </span>
      </div>
    </div>
  );
}

export default Header;