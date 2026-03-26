# Full Demo
[![Watch Demo](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=DB2yZ_J1tjg)

# Live F1 Telemetry Dashboard
## Project description
This is a simple FastAPI - ReactJs project that aims to mimic the real life F1 Live Timing website. F1 Live Timing is the official website/system created by Formula 1 which displays live race data such as driver leaderboard, driver tracking, individual car telemetry data (speed, gear, rpm, etc). Like the real system, this counterpart displays the "live" race data running in the game (F1 2020) to the front-end.

## How it works
It uses the existing ```f1-2020-telemetry``` python package to get the running binary data from the game and unpack it. Once unpacked, it deconstructs the packets according to its predefined packet structure (more info about this [here](https://f1-2020-telemetry.readthedocs.io/en/latest/)). The game broadcasts the data on localhost at port 20777 and the telemetry_parser tries to connect to it and listen for data. It receives the data, unpacks it using the library and sends 4 SPECIFIC CATEGORIES of data to the frontend (participants, lap data, player car telemetry and motion data). Each of these packets arrive at different frequencies - some configurable in the game settings and some locked to a specific frequency to save bandwidth. This data is then sent to the FastAPI app via an asynchronous queue to which the frontend listens to receive the data and display. 