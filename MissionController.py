import exceptions
import socket
import os
import time
import sys
import json
import argparse
import re
import math

import dronekit
from dronekit import LocationGlobal

from util import Util
from Drone import DroneController
import thread
util = Util()

parser = argparse.ArgumentParser(description='This module acts as a message broker and mission controller between UDP Client and ArduCopter.')
#parser.add_argument('--client', help="Type in client host and port in form HOST:PORT")
#parser.add_argument('--server', help="Type in server host and port in form HOST:PORT")
parser.add_argument('--drone_address', help="Set connection string to drone (or SITL)")


class MissionController(object):
    def __init__(self,UDP_IP="127.0.0.1",HOST_PORT=5005,CLIENT_PORT=5006,drone_address=""):
    
        """ This module acts as a message broker and mission controller between UDP Client and ArduCopter.
            It takes as a parameters 
        """
        self.host = UDP_IP
        self.port = HOST_PORT
        self.HOST_SERVER_ADDRESS = (UDP_IP,HOST_PORT)
        self.NODE_SERVER_ADDRESS =(UDP_IP,CLIENT_PORT)


        self.controller = DroneController(connection_string=drone_address)
        try:
            self.controller.connect()
            pass
        # Bad TCP connection
        except socket.error:
            print('No server exists!')
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
        print("Starting socket server.")
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
                self.router_callback(datagram)
            if "DONE" == datagram:
                break

    def router_callback(self,data):
        #Remove the EOF characters
        data =re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', data)

        dt = util.json_loads_byteified(data)
        payload = {}
        if dt.get('type')=="Launch":
            self.controller.launch()
            payload ={"Operation":"Launch","Status":"Success"}

        if dt.get('type') == "TakeOff":
            self.controller.takeoff(20)
            self.check_if_took_off(20)



        elif dt.get("type")=="Land":
            print("Landing procedure command received")
            self.controller.land()
            thread.start_new_thread(self.check_if_landed,())

        elif dt.get('type')=="GoTo":
            try:
                tmp = dt.get("data")
                tmp = tmp.get("latlong")
                self.controller.goto(tmp,30)
                tmp = self.controller.getLocationGlobal(tmp[0], tmp[1])
                thread.start_new_thread(self.check_if_target_reached, (tmp,))
            except Exception as Err:
                print (Exception.message)

        elif dt.get('type')=="Status":
            if self.controller:
                payload =self.prepareStatusMsg()
            else:
                payload = {"GPS":"Test","Bat":200}

        self.sendMessage(data=payload)
     
    def check_if_landed(self):
        while True:
            if not self.controller.vehicle.armed:
                self.sendMessage(data={"Operation":"Land","Status":"Success"})
                self.controller.change_mode("GUIDED")
                break
            else:
                print("Landing...")
                time.sleep(1.5)


    def check_if_took_off(self, target_altitude):

        while True:
            print(" Altitude: ", self.controller.vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if self.controller.vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
                print("Reached target altitude")
                self.sendMessage(data={"Operation":"TakeOff","Status":"Success"})
                break
            time.sleep(1.5)


    def check_if_target_reached(self,targetLocation):
         
        def get_distance_metres(aLocation1, aLocation2):
            """
            Returns the ground distance in metres between two LocationGlobal objects.
            It comes from the ArduPilot test code.
            """
            dlat = aLocation2.lat - aLocation1.lat
            dlong = aLocation2.lon - aLocation1.lon
            return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

        while self.controller.vehicle.mode.name=="GUIDED":
             #Stop action if we are no longer in guided mode.
            #targetDistance = get_distance_metres(self.controller.getLocationGlobal(targetLocation[0],targetLocation[1]),self.controller.getLocationGlobal(targetLocation))
            remainingDistance=get_distance_metres(self.controller.vehicle.location.global_relative_frame,
                                                  targetLocation)
            print("Distance to target: ", remainingDistance)
            if remainingDistance<=1:
                print("Reached target")
                self.sendMessage(data={"Operation":"GoTo","Status":"Success"})
                break
            else:
                time.sleep(2)


    def prepareStatusMsg(self):
        try:
            return {"bat":self.controller.vehicle.battery.__str__(),
                "gps":self.controller.vehicle.gps_0.__str__(),
                "alt":self.controller.altitude.__str__(),
                "loc":self.controller.vehicle.location.global_frame.__str__(),
                "mode":self.controller.vehicle.mode.__str__(),
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
            print("Send failed. Waiting for server. "+ err.message)

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


