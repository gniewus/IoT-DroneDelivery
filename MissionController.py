from __future__ import print_function
import socket
import os
import time
import sys
import json
import argparse
import re
from util import Util
from Controller import DroneController
import thread
util = Util()

parser = argparse.ArgumentParser(description='This module acts as a message broker and mission controller between UDP Client and ArduCopter.')
#parser.add_argument('--client', help="Type in client host and port in form HOST:PORT")
#parser.add_argument('--server', help="Type in server host and port in form HOST:PORT")
parser.add_argument('--drone_address', help="Set connection string to drone (or SITL)")

ctrl = None #DroneController('udp:127.0.0.1:14550')

class MissionController(object):
    def __init__(self,UDP_IP="127.0.0.1",HOST_PORT=5005,CLIENT_PORT=5006,drone_address=""):
    
        """ This module acts as a message broker and mission controller between UDP Client and ArduCopter.
            It takes as a parameters 
        """
        self.host = UDP_IP
        self.port = HOST_PORT
        self.HOST_SERVER_ADDRESS = (UDP_IP,HOST_PORT)
        self.NODE_SERVER_ADDRESS =(UDP_IP,CLIENT_PORT)

        print("Connecting to "+ drone_address)
        self.controller = DroneController(connection_string=drone_address)
        try:
            self.controller.connect()
            pass
        # Bad TCP connection
        except socket.error:
            print
            'No server exists!'
        # Bad TTY connection
        except exceptions.OSError as e:
            print
            'No serial exists!'
        # API Error
        except dronekit.APIException:
            print
            'Timeout!'
        # Other error
        except Exception as e:
            print('Some other error!'+e.message)
        

       
        
    def run_udp_socket_server(self,host=None,port=None):
        
        self.run_udp_client()
        if host and port:
            self.host = host;
            self.port = port;
        print("starting unix domain socket server.")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.host,self.port))
        print("Listening on path: %s:%s" % (self.host,self.port))
        
        thread.start_new_thread(self.broadcast_status,())
        while True:
            datagram = self.server.recv(1024)
            if not datagram:
                break
            else:
                print("-" * 20)
                print(datagram)
                self._data_callback(datagram)
            if "DONE" == datagram:
                break

    def _data_callback(self,data):
        data =re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', data)
        
        dt = util.json_loads_byteified(data)
        payload = {}
        if dt.get('type')=="Launch":
            print("Launchig procedure comand received")
            thread.start_new_thread(self.controller.launch,())
            pass
        elif dt.get("type")=="Land":
            print("Launching procedure command received") 
            self.controller.land()
        elif dt.get('type')=="GoTo":
            tmp = dt.get("data")
            tmp = tmp.get("latlong")
            print(tmp,tmp[0])
            
            self.controller.goto(tmp,30)
        elif dt.get('type')=="Status":
            if self.controller:
                payload =self.prepareStatusMsg()
            else:
                payload = {"GPS":"Test","Bat":200}

        self.sendMessage(data=payload)

    def prepareStatusMsg(self):
        try:
            return {"bat":self.controller.vehicle.battery.__str__(),
                "gps":self.controller.vehicle.gps_0.__str__(),
                "alt":self.controller.altitude.__str__(),
                "loc":self.controller.vehicle.location.global_frame.__str__(),
                "airspeed": self.controller.vehicle.airspeed.__str__(),
                "groundspeed":self.controller.vehicle.airspeed.__str__()
                }   
        except AttributeError as err:
            return{"message":"Device not ready "}
            

    def sendMessage(self,type='message',data={}):
        try:
            dump = json.dumps({"type":"message",'data':data})
            self.server.sendto(dump+"\f",self.NODE_SERVER_ADDRESS)
        except AttributeError as err:
            print("Send failed. Waiting for server. ")
            pass
    def broadcast_status(self):
        while True:
            msg = self.prepareStatusMsg()
            self.sendMessage(type="Status",data=msg)
            time.sleep(1)

    def closeServer(self):
        print("-" * 20)
        print("Server is shutting down now...")
        self.server.close()
        os.remove(self.server_path)
        print("Server shutdown and path removed.")

    def run_udp_client(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)




if __name__ == '__main__':
    args = parser.parse_args()
    if args.drone_address:
        ms = MissionController(drone_address=args.drone_address)
    else:    
        ms = MissionController()
    
    ms.run_udp_socket_server()

    
    
    
