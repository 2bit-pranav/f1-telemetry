import socket
import json
from f1_2020_telemetry.packets import unpack_udp_packet
import asyncio

MY_IP = "127.0.0.1"
GAME_PORT = 20777
TIMEOUT = 10.0

def start_telemetry_loop(telemetry_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
    # flag for participants data (to be sent only once)
    once_flag = False
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

            # PACKET 4: PARTICIPANTS (ONE-TIME)
            if once_flag is not True and packet.header.packetId == 4:
                once_flag = True
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
                lap_data = []

                raw_data = packet.lapData
                for i in range(0, 20):
                    lt = raw_data[i].currentLapTime
                    s1 = raw_data[i].sector1TimeInMS / 1000.0
                    s2 = raw_data[i].sector2TimeInMS / 1000.0
                    s3 = lt - (s1 + s2)
                    td = raw_data[i].totalDistance
                    p = raw_data[i].carPosition

                    lap_data.append(
                        {
                            "i": i,
                            "p": p,
                            "s1": s1,
                            "s2": s2,
                            "s3": s3,
                            "lt": lt,
                            "td": td,
                        }
                )

                lap_telemetry = {
                    "type": "lap_telemetry",
                    "data": lap_data,
                }

                json_msg = json.dumps(lap_telemetry) + "\n"
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

        except socket.timeout:
            print("### NO DATA FROM GAME ###")
            continue

        except KeyboardInterrupt:
            break
    
    game_socket.close()