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

parser = argparse.ArgumentParser(description='This module acts as a message broker and controller between UDP Client and ArduCopter.')
parser.add_argument('--client', help="Type in client host and port in form HOST:PORT")
parser.add_argument('--server', help="Type in server host and port in form HOST:PORT")
parser.add_argument('--drone_address', help="Set connection string to drone (or SITL)")

ctrl = None #DroneController('udp:127.0.0.1:14550')

class UnixSocket(object):
    def __init__(self,UDP_IP="127.0.0.1",HOST_PORT=5005,CLIENT_PORT=5006):
        self.host = UDP_IP
        self.port = HOST_PORT

        self.HOST_SERVER_ADDRESS = (UDP_IP,HOST_PORT)
        self.NODE_SERVER_ADDRESS =(UDP_IP,CLIENT_PORT)
        
    def run_unix_domain_socket_server(self,host=None,port=None):
        self.controller = ctrl
        self.controller.connect()
        self.run_udp_client()
        if host and port:
            self.host = host;
            self.port = port;
        print("starting unix domain socket server.")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.host,self.port))
        print("Listening on path: %s:%s" % (self.host,self.port))
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
            ctrl.connect()
            thread.start_new_thread(ctrl.launch,())
            pass
        elif dt.get("type")=="Land":
            print("Launching procedure command received") 
            ctrl.land()
        elif dt.get('type')=="GoTo":
            print(dt.get("data"))
            ctrl.goto([52.516783, 13.323896],30)
        elif dt.get('type')=="Status":
            print("Status")
            if self.controller:
                payload ={"bat":ctrl.vehicle.battery.__str__(),
                "gps":ctrl.vehicle.gps_0.__str__(),
                "alt":ctrl.altitude.__str__(),
                "loc":ctrl.vehicle.location.global_frame.__str__(),
                "airspeed": ctrl.vehicle.airspeed.__str__()
                }
            else:
                payload = {"GPS":"Test","Bat":200}

        self.sendMessage(data=payload)
            
    def sendMessage(self,type='message',data={}):
            dump = json.dumps({"type":"message",'data':data})
            self.server.sendto(dump+"\f",self.NODE_SERVER_ADDRESS)

    def closeServer(self):
        print("-" * 20)
        print("Server is shutting down now...")
        self.server.close()
        os.remove(self.server_path)
        print("Server shutdown and path removed.")

    def run_udp_client(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def sendStats(self,object):
        obj = json.dumps(object)
        self.sock.sendall(obj)



if __name__ == '__main__':
    args = parser.parse_args()
    if args.drone_address:
        print (args.drone_address+" was given")
        ctrl = DroneController(connection_string=str(args.drone_address))
    else:    
        ctrl = DroneController()
    us = UnixSocket()
    us.run_unix_domain_socket_server()

def _parseParameter(el):
    try:
        host = el.split[":"][0]
        port = el.split[":"][1]
        return (host,port)
    except Exception as err:
        return None
        pass
    
    
    
