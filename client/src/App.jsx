import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import TimingTower from "./components/TimingTower";
import CarTelemetry from "./components/CarTelemetry";
import {
    dummyHeader,
    dummyDrivers,
    dummyTelemetry1,
    dummyTelemetry2,
} from "./dummy_data";
import "./App.css";

const USE_DUMMY_DATA = true;

function App() {
    const [isConnected, setIsConnected] = useState(false);
    const [drivers] = useState([]);
    const [selectedDrivers, setSelectedDrivers] = useState([null, null]);

    useEffect(() => {
        if (USE_DUMMY_DATA) return;

        const ws = new WebSocket("ws://127.0.0.1:8000/ws/race");
        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => setIsConnected(false);

        ws.onmessage = () => {
            // Future backend parsing logic
        };

        return () => ws.close();
    }, []);

    const activeHeader = USE_DUMMY_DATA
        ? dummyHeader
        : { track: "Waiting for connection...", lap: "--", isConnected };
    const activeDrivers = USE_DUMMY_DATA ? dummyDrivers : drivers;

    const telSlot1 = USE_DUMMY_DATA ? dummyTelemetry1 : selectedDrivers[0];
    const telSlot2 = USE_DUMMY_DATA ? dummyTelemetry2 : selectedDrivers[1];

    const handleDriverClick = (driver) => {
        if (USE_DUMMY_DATA) return;

        setSelectedDrivers((prev) => {
            if (!prev[0]) return [driver, prev[1]];
            if (!prev[1]) return [prev[0], driver];
            return [prev[1], driver];
        });
    };

    return (
        <div className="dashboard">
            <Header
                track={activeHeader.track}
                lap={activeHeader.lap}
                isConnected={activeHeader.isConnected}
            />

            <div className="main-content">
                {!USE_DUMMY_DATA && activeDrivers.length === 0 ? (
                    <div
                        className="timing-tower-container"
                        style={{
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            color: "#666",
                        }}
                    >
                        <h2>Waiting for telemetry stream...</h2>
                    </div>
                ) : (
                    <TimingTower
                        drivers={activeDrivers}
                        onDriverClick={handleDriverClick}
                    />
                )}

                <div className="telemetry-sidebar">
                    <CarTelemetry data={telSlot1} />
                    <CarTelemetry data={telSlot2} />
                </div>
            </div>
        </div>
    );
}

export default App;
