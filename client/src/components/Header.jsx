import React from "react";

function Header({ isConnected }) {
    return (
        <div className="header">
            <div className="race-info">
                <h1>British Grand Prix - Silverstone</h1>
                <p>Lap 2 / 52</p>
            </div>

            <div className="connection-status">
                {/* Conditional rendering: Shows different text/color based on connection state */}
                <span
                    className="status-indicator"
                    style={{ color: isConnected ? "#00ff00" : "#ff0000" }}
                >
                    {isConnected ? "🟢 Live" : "🔴 Disconnected"}
                </span>
            </div>
        </div>
    );
}

export default Header;
