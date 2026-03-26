import React, { useState, useEffect, useRef } from "react";
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

const USE_DUMMY_DATA = false;

const getTeamName = (id) => {
    const teams = {
        0: "Mercedes",
        1: "Ferrari",
        2: "Red Bull Racing",
        3: "Williams",
        4: "Racing Point",
        5: "Renault",
        6: "AlphaTauri",
        7: "Haas",
        8: "McLaren",
        9: "Alfa Romeo",
    };
    return teams[id] || "Unknown Team";
};

function App() {
    const [isConnected, setIsConnected] = useState(false);
    const [timingTowerData, setTimingTowerData] = useState([]);
    const [playerTelemetry, setPlayerTelemetry] = useState(null);
    const driverMapRef = useRef({});

    useEffect(() => {
        if (USE_DUMMY_DATA) return;

        const ws = new WebSocket("ws://127.0.0.1:8000/ws/race");
        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => setIsConnected(false);

        ws.onmessage = (event) => {
            // display dummy
            if (USE_DUMMY_DATA) return;

            // console.log("📥 Raw data received from WebSocket:", event.data);

            // backend logic
            const packet = JSON.parse(event.data);

            // PARTICIPANTS DATA
            if (packet.type === "player_telemetry") {
                const newMap = {};
                packet.participants.forEach((p) => {
                    newMap[p.index] = {
                        name: p.name,
                        raceNum: p.raceNum,
                        teamId: p.teamId,
                        teamName: getTeamName(p.teamId),
                    };
                });
                // save to ref
                driverMapRef.current = newMap;
            }

            // LAP DATA
            else if (packet.type === "lap_telemetry") {
                // safe-check
                if (Object.keys(driverMapRef.current).length === 0) return;

                const updatedData = packet.data.map((rawLap) => {
                    const driverInfo = driverMapRef.current[rawLap.i] || {};
                    return {
                        ...driverInfo, // adds i, p, s1, s2, s3, lt, td
                        ...rawLap, // adds name, raceNum, teamId, teamName
                    };
                });
                // save to state
                setTimingTowerData(updatedData);
            }

            // CAR TELEMETRY (player car only)
            else if (packet.type === "car_telemetry") {
                setPlayerTelemetry({
                    ...packet, // this one does not have type, data structure so include packet directly
                    name: "PLAYER CAR",
                    raceNum: "--",
                    teamName: "--",
                    teamId: 10, // unknown team
                });
            }

            // MOTION DATA (not used yet, to be used for track map)
            // ...
        };

        return () => ws.close();
    }, []);

    const activeHeader = USE_DUMMY_DATA
        ? dummyHeader
        : { track: "Live F1 Session", lap: "--", isConnected };
    const activeDrivers = USE_DUMMY_DATA ? dummyDrivers : timingTowerData;
    const telSlot1 = USE_DUMMY_DATA ? dummyTelemetry1 : "disabled";
    const telSlot2 = USE_DUMMY_DATA ? dummyTelemetry2 : playerTelemetry // to be implemented

    const handleDriverClick = () => {
        if (USE_DUMMY_DATA) return;
        // to be implemented
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
