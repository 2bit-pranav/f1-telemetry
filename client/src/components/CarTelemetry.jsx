import React from "react";
import { TEAM_COLORS } from "../constants";

function CarTelemetry({ data }) {
    if (!data) {
        return (
            <div className="telemetry-card">
                <div className="telemetry-placeholder">
                    Click on a driver to view telemetry
                </div>
            </div>
        );
    }

    const throttle = data.t || 0;
    const brake = data.b || 0;
    const speed = data.s || 0;
    const gear = data.g || 0;
    const rpm = data.rpm || 0;
    const drsEnabled = data.drs === 1;
    const teamColor = TEAM_COLORS[data.teamId] || "#aaa";

    return (
        <div className="telemetry-card">
            <div className="tel-header">
                <div>
                    <span
                        style={{
                            color: teamColor,
                            fontSize: "0.85rem",
                            fontWeight: "bold",
                        }}
                    >
                        {data.teamName}
                    </span>
                    <h2>{data.name}</h2>
                </div>
                <div className="tel-number" style={{ color: teamColor }}>
                    {data.raceNum}
                </div>
            </div>

            <div className="input-row">
                <span>Throttle</span>
                <div className="bar-bg">
                    <div
                        className="bar-fill throttle-fill"
                        style={{ width: `${throttle * 100}%` }}
                    ></div>
                </div>
            </div>

            <div className="input-row">
                <span>Brake</span>
                <div className="bar-bg">
                    <div
                        className="bar-fill brake-fill"
                        style={{ width: `${brake * 100}%` }}
                    ></div>
                </div>
            </div>

            <div className="tel-stats">
                <div className="stat-box">
                    <span className="label">Speed (km/h)</span>
                    <span className="value">{speed}</span>
                </div>
                <div className="stat-box">
                    <span className="label">Gear</span>
                    <span className="value">{gear}</span>
                </div>
                <div className="stat-box">
                    <span className="label">RPM</span>
                    <span className="value">{rpm}</span>
                </div>
                <div className="stat-box">
                    <span className="label">DRS</span>
                    <span
                        className={`value ${drsEnabled ? "drs-on" : "drs-off"}`}
                    >
                        {drsEnabled ? "ON" : "OFF"}
                    </span>
                </div>
            </div>
        </div>
    );
}

export default CarTelemetry;
