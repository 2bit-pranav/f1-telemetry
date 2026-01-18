import socket
import json
from f1_2020_telemetry.packets import unpack_udp_packet

MY_IP = "127.0.0.1"
UDP_PORT = 20777
JAVA_PORT = 8081
TIMEOUT = 10.0

def main():
  # this is for sending participants data
  once_flag = False
  # throttle motion data to improve bandwidth
  motion_count = 0

  # step 1. establish conn with game at ip, port [UDP]
  game_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  game_socket.bind((MY_IP, UDP_PORT))
  game_socket.settimeout(TIMEOUT)

  # step 2. establish conn with java backend at ip, port [TCP]
  java_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
  try:
    java_socket.connect((MY_IP, JAVA_PORT))
    print("connected to java backend")
  except ConnectionRefusedError:
    print("failed to connect to java backend")
    exit()

  # step 3. send data while conn exists
  while True:
    try:
      # step 3.1 unpack packet
      udp_packet = game_socket.recv(2048)
      packet = unpack_udp_packet(udp_packet)

      # PACKET 4: PARTICIPANTS (ONE-TIME)
      if once_flag != True and packet.header.packetId == 4:
        once_flag = True
        participants = []
        
        for i in range(0, 20):
          player = packet.participants[i]
          name = player.name.decode("utf-8").rstrip("\x00")
          teamId = player.teamId
          raceNum = player.raceNumber

          participants.append({"index": i, "raceNum": raceNum, "name": name, "teamId": teamId})

        player_telemetry = {
          "type": "player_telemetry",
          "participants": participants
        }

        json_msg = json.dumps(player_telemetry) + "\n"
        # print(json_msg)
        
        try:
          java_socket.sendall(json_msg.encode("utf-8"))
        except BrokenPipeError:
          print("connection to backend lost")

      # PACKET 2: LAP DATA
      elif packet.header.packetId == 2:
        lap_data = []

        raw_data = packet.lapData
        for i in range(0, 20):
          lt = raw_data[i].currentLapTime
          s1 = raw_data[i].sector1TimeInMS/1000.0  # convert to sec
          s2 = raw_data[i].sector2TimeInMS/1000.0  # convert to sec
          s3 = lt - (s1 + s2)
          td = raw_data[i].totalDistance
          p = raw_data[i].carPosition

          lap_data.append({
            "i": i,
            "p": p,
            "s1": s1,
            "s2": s2,
            "s3": s3,
            "lt": lt,
            "td": td
          })

        lap_telemetry = {
          "type": "lap_telemetry",
          "data": lap_data
        }

        json_msg = json.dumps(lap_telemetry) + "\n"
        # print(json_msg)

        try:
          java_socket.sendall(json_msg.encode("utf-8"))
        except BrokenPipeError:
          print("connection to backend lost")
        
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
          "drs": car_data.drs
        }

        json_msg = json.dumps(car_telemetry) + " \n"
        # print(json_msg)

        try:
          java_socket.sendall(json_msg.encode("utf-8"))
        except BrokenPipeError:
          print("connection to backend lost")

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

          motion_data.append({
            "i": i,
            "x": x,
            "z": z
          })

        motion_telemetry = {
          "type": "motion_telemetry",
          "data": motion_data
        }

        json_msg = json.dumps(motion_telemetry) + "\n"
        # print(json_msg)

        try:
          java_socket.sendall(json_msg.encode("utf-8"))
        except BrokenPipeError:
          print("connection to backend lost")

    except socket.timeout:
      print("### NO DATA ###")
      continue

    except KeyboardInterrupt:
      break

  game_socket.close()
  java_socket.close()


if __name__ == "__main__":
  main()