


This repository includes:
- Python (dronekit) drone controller app
- Python UDP server/client wrapper
- NodeJS UDP server/client connector

```
pip install -r requirements.txt
```
Starting DroneController:

``` python MissionController.py  ```

Mission controller takes ```--drone_address``` parameter which should be a UDP/TCP MavLink connection string. Eighter directly from the ArduCopter or through mavproxy.py


Starting NodeUDP Connector

``` node Connector.js ```


Ernst-Reuter:52.512904, 13.322384


```$ dronekit-sitl copter --home 52.512904,13.322384,30,354  ```

```$ sim_vehicle --l 52.512904,13.322384,30,354  -mode quad```

