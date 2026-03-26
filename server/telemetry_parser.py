import socket
import json
from f1_2020_telemetry.packets import unpack_udp_packet
import asyncio

MY_IP = "127.0.0.1"
GAME_PORT = 20777
TIMEOUT = 10.0

def start_telemetry_loop(telemetry_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
    # simple counter for motion data (to be sent on every 6th increment)
    motion_count = 0

    game_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_socket.bind((MY_IP, GAME_PORT))
    game_socket.settimeout(TIMEOUT)

    print("### LISTENING FOR GAME DATA ###")

    while True:
        try:
            udp_packet = game_socket.recv(2048)
            packet = unpack_udp_packet(udp_packet)

            # PACKET 4: PARTICIPANTS
            if packet.header.packetId == 4:
                participants = []

                for i in range(0, 20):
                    player = packet.participants[i]
                    name = player.name.decode("utf-8").rstrip("\x00")
                    teamId = player.teamId
                    raceNum = player.raceNumber

                    participants.append(
                        {
                            "index": i,
                            "raceNum": raceNum,
                            "name": name,
                            "teamId": teamId,
                        }
                    )

                player_telemetry = {
                    "type": "player_telemetry",
                    "participants": participants,
                }

                json_msg = json.dumps(player_telemetry) + "\n"
                loop.call_soon_threadsafe(telemetry_queue.put_nowait, json_msg)

            # PACKET 2: LAP DATA
            elif packet.header.packetId == 2:
                raw_data = packet.lapData
                extracted_cars = []
                
                # 1. Extract and calculate Sector "Tick" Logic
                for i in range(0, 20):
                    p = raw_data[i].carPosition
                    td = raw_data[i].totalDistance
                    c_lap = raw_data[i].currentLapTime
                    lt = raw_data[i].lastLapTime # Use the ACTUAL last lap time
                    
                    s1_ms = raw_data[i].sector1TimeInMS
                    s2_ms = raw_data[i].sector2TimeInMS
                    
                    if s1_ms == 0:
                        # Car is currently IN Sector 1
                        s1 = c_lap
                        s2 = 0.0
                        s3 = 0.0
                    elif s2_ms == 0:
                        # Car is currently IN Sector 2
                        s1 = s1_ms / 1000.0
                        s2 = c_lap - s1
                        s3 = 0.0
                    else:
                        # Car is currently IN Sector 3
                        s1 = s1_ms / 1000.0
                        s2 = s2_ms / 1000.0
                        s3 = c_lap - (s1 + s2)
                        
                    extracted_cars.append({
                        "i": i, "p": p, "s1": s1, "s2": s2, "s3": s3, "lt": lt, "td": td
                    })
                
                # 2. Sort the grid by Position to calculate Intervals
                sorted_cars = sorted(extracted_cars, key=lambda x: x["p"])
                
                for idx, car in enumerate(sorted_cars):
                    # P1 gets the 'Leader' tag (interval = 0.0)
                    if car["p"] == 1 or idx == 0:
                        car["interval"] = 0.0
                    else:
                        # P2-P20 calculate interval to the car directly ahead
                        car_ahead = sorted_cars[idx - 1]
                        dist_gap = car_ahead["td"] - car["td"]
                        
                        # Time = Distance / Speed (75 m/s is a solid F1 baseline)
                        car["interval"] = max(0.0, dist_gap / 75.0) 

                lap_telemetry = {
                    "type": "lap_telemetry",
                    "data": sorted_cars, # We send the pre-sorted list!
                }

                json_msg = json.dumps(lap_telemetry)
                loop.call_soon_threadsafe(telemetry_queue.put_nowait, json_msg)

            # PACKET 6: CAR TELEMETRY (PLAYER ONLY)
            elif packet.header.packetId == 6:
                player_idx = packet.header.playerCarIndex
                car_data = packet.carTelemetryData[player_idx]

                car_telemetry = {
                    "type": "car_telemetry",
                    "t": round(car_data.throttle, 2),
                    "b": round(car_data.brake, 2),
                    "s": car_data.speed,
                    "g": car_data.gear,
                    "rpm": car_data.engineRPM,
                    "drs": car_data.drs,
                }

                json_msg = json.dumps(car_telemetry) + "\n"
                loop.call_soon_threadsafe(telemetry_queue.put_nowait, json_msg)

            # PACKET 0: MOTION DATA (FOR TRACK MAP)
            elif packet.header.packetId == 0:
                motion_count += 1

                if motion_count % 6 != 0:
                    continue

                motion_data = []

                raw_data = packet.carMotionData
                for i in range(0, 20):
                    x = raw_data[i].worldPositionX
                    z = raw_data[i].worldPositionZ

                    motion_data.append(
                        {
                            "i": i,
                            "x": x,
                            "z": z,
                        }
                    )

                motion_telemetry = {
                    "type": "motion_telemetry",
                    "data": motion_data,
                }

                json_msg = json.dumps(motion_telemetry) + "\n"
                loop.call_soon_threadsafe(telemetry_queue.put_nowait, json_msg)
                print("### SENDING DATA ###")

        except socket.timeout:
            print("### NO DATA FROM GAME ###")
            continue

        except KeyboardInterrupt:
            break
    
    game_socket.close()