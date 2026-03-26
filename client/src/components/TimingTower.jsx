import React from "react";
import { TEAM_COLORS } from "../constants";

function TimingTower({ drivers, onDriverClick }) {
    return (
        <div className="timing-tower-container">
            <table className="timing-table">
                <thead>
                    <tr>
                        <th>POS</th>
                        <th>DRIVER</th>
                        <th>TEAM</th>
                        <th>INTERVAL</th>
                        <th>S1</th>
                        <th>S2</th>
                        <th>S3</th>
                        <th>LAST LAP</th>
                    </tr>
                </thead>
                <tbody>
                    {[...drivers]
                        .sort((a, b) => a.p - b.p)
                        .map((driver, index) => {
                            const teamColor =
                                TEAM_COLORS[driver.teamId] || "#fff";

                            return (
                                <tr
                                    key={driver.i}
                                    onClick={() => onDriverClick(driver)}
                                >
                                    <td>{driver.p || index + 1}</td>

                                    <td>
                                        <span
                                            style={{
                                                color: teamColor,
                                                fontWeight: "bold",
                                                marginRight: "8px",
                                            }}
                                        >
                                            {driver.raceNum}
                                        </span>
                                        <span style={{ color: "#fff" }}>
                                            {driver.name}
                                        </span>
                                    </td>

                                    <td>
                                        <span
                                            style={{
                                                color: teamColor,
                                                fontWeight: "500",
                                            }}
                                        >
                                            {driver.teamName}
                                        </span>
                                    </td>

                                    <td>
                                        {driver.p === 1
                                            ? "Leader"
                                            : `+${(driver.interval || 0).toFixed(3)}`}
                                    </td>

                                    <td>
                                        {driver.s1
                                            ? driver.s1.toFixed(3)
                                            : "--"}
                                    </td>
                                    <td>
                                        {driver.s2
                                            ? driver.s2.toFixed(3)
                                            : "--"}
                                    </td>
                                    <td>
                                        {driver.s3
                                            ? driver.s3.toFixed(3)
                                            : "--"}
                                    </td>
                                    <td>
                                        {driver.lt
                                            ? driver.lt.toFixed(3)
                                            : "--"}
                                    </td>
                                </tr>
                            );
                        })}
                </tbody>
            </table>
        </div>
    );
}

export default TimingTower;
