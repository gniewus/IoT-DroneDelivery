

## Overview

This repository includes:
- Python (dronekit) drone controller app
- Python UDP server/client wrapper
- NodeJS UDP server/client connector

![Alt text](NavioControllerDiagram.jpg?raw=true "Diagram")




```
pip install -r requirements.txt
```
Starting DroneController:

``` python MissionController.py  ```

Mission controller takes ```--drone_address``` parameter which should be a UDP/TCP MavLink connection string (in form protocol:host:port). Eighter directly from the ArduCopter or through mavproxy.py

Starting NodeUDP Connector

``` node Connector.js ```

After booting up and successfully connecting to the drone, MissionController listens to UDP port for incoming messages from NodeServer.
In background it sends every second a complete list of drone parameters in JSON format.




## Misc commands
Ernst-Reuter:52.512904, 13.322384

```$ dronekit-sitl copter --home 52.512904,13.322384,30,354  ```

```$ sim_vehicle --l 52.512904,13.322384,30,354  --mode quad```

```$ sim_vehicle --l TEL --no-mavproxy --mode quad```

