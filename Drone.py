from __future__ import print_function
import dronekit
import socket
import exceptions
from dronekit import VehicleMode, LocationGlobal, LocationGlobalRelative
import time

class DroneController(object):
    def __init__(self, connection_string=None,vehicle=dronekit.Vehicle):
        if connection_string:
            self.connection_string = connection_string;
        else:
            self.connection_string = self._start_SITL()        
        
        self.vehicle= vehicle
        self.mission_start_location=[]
        
    def _log(self, message):
        print("[DEBUG]: {0}".format(message))

    def connect(self):
        self.gps_lock = False
        self.altitude = 0.0
        self.current_status ={}
    
        self.vehicle = dronekit.connect(self.connection_string, heartbeat_timeout=15, wait_ready=True)
        # Connect to the Vehicle
        self._log('Connected to vehicle.')
        self.commands = self.vehicle.commands
        self.current_coords = []
        # Get Vehicle Home location - will be `None` until first set by autopilot
        while not self.vehicle.home_location:
            self.cmds = self.vehicle.commands
            self.cmds.download()
            self.cmds.wait_ready()
            if not self.vehicle.home_location:
                self._log(" Waiting for home location...")
            time.sleep(2)
        self.mission_start_location=[self.vehicle.home_location.lat,self.vehicle.home_location.lat]
        self._log("Drone app started")


    def takeoff(self,aTargetAltitude=30):
        self.arm()
        self._log("Taking off")

        # Register observers
        self.vehicle.add_attribute_listener('location', self.location_callback)
        #self.vehicle.add_attribute_listener('mode', self.mode_callback)

        self.vehicle.simple_takeoff(aTargetAltitude)
        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after self.vehicle.simple_takeoff will execute immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

        time.sleep(30)
        
    def mode_callback(self,attribute_name,x,y):
        if self.vehicle.mode != "GUIDED":
            print(self.vehicle.mode)
            self._log("Unexpeced mode change from GUIDED, aborting the operation")
            self._stop()


    def change_mode(self, mode):
        self._log("Changing to mode: {0}".format(mode))

        self.vehicle.mode = VehicleMode(mode)
        while self.vehicle.mode.name != mode:
            self._log('  ... polled mode: {0}'.format(mode))
            time.sleep(1)

    def goto(self, location, relative=None):
        self._log("Goto: {0}, {1}".format(location, self.altitude))

        if relative:
            self.vehicle.simple_goto(
                LocationGlobalRelative(
                    float(location[0]), float(location[1]),
                    float(self.altitude)
                )
            )
        else:
            self.vehicle.simple_goto(
                LocationGlobal(
                    float(location[0]), float(location[1]),
                    float(self.altitude)
                )
            )
    
        self.vehicle.flush()

    def get_location(self):
        return [self.current_location.lat, self.current_location.lon]

    def location_callback(self, vehicle, name, location):
        if location.global_relative_frame.alt is not None:
            self.altitude = location.global_relative_frame.alt
        #self.current_status= self._print_stats(True)
        self.current_location = location.global_relative_frame

    def arm(self, value=True):
        if value:
            self._log('Waiting for arming...')
            self.vehicle.armed = True
            while not self.vehicle.armed:
                time.sleep(.1)
        else:
            self._log("Disarming!")
            self.vehicle.armed = False

    def land(self):
        self._log("Changing mode to LAND")
        self.change_mode("LAND")
        self._log("Landing...")

    def launch(self):
        self._log("Waiting for location...")
        while self.vehicle.location.global_frame.lat == 0:
            time.sleep(0.1)
        self.home_coords = [self.vehicle.location.global_frame.lat,
                            self.vehicle.location.global_frame.lon]

        self._log("Waiting for ability to arm...")
        while not self.vehicle.is_armable:
            time.sleep(.1)

        self._log('Running initial boot sequence')
        self.change_mode('GUIDED')
        self.takeoff()

    def _print_stats(self, dump=False):
        # Get some vehicle attributes (state)
        if not dump:
            print("Get some vehicle attribute values:")
            print(" GPS: %s" % self.vehicle.gps_0)
            print(" Battery: %s" % self.vehicle.battery)
            print(" Last Heartbeat: %s" % self.vehicle.last_heartbeat)
            print(" Is Armable?: %s" % self.vehicle.is_armable)
            print(" System status: %s" % self.vehicle.system_status.state)
            print(" Mode: %s" % self.vehicle.mode.name)  # settable
        else:
            return {"GPS": str(self.vehicle.gps_0),
                    "Batt": str(self.vehicle.battery),
                    "Altitude":str(self.altitude),
                    "Coords": self.get_location()
                    }

    def _start_SITL(self):
        import dronekit_sitl
        sitl = SITL()
        print("sdsaass"*20)
        sitl.download("copter", "3.5", verbose=False) # ...or download system (e.g. "copter") and version (e.g. "3.3")
        sitl.launch(args, verbose=False, await_ready=False, restart=False)
        sitl.block_until_ready(verbose=False) # explicitly wait until receiving commands
        code = sitl.complete(verbose=False) # wait until exit
        connection_string = sitl.connection_string()
        return connection_string

    def _stop(self):
        self.vehicle.close()


""" class Command(Thread):
    def __init__(self, type):
        ''' Constructor. '''
 
        Thread.__init__(self)
        self.command = type
        payload = {}
        if self.command=="Launch":
            print("Launchig procedure comand received")
            ctrl.connect()
            thread.start_new_thread(ctrl.launch,())
            pass
        elif self.command=="GoTo":
            print(dt.get("data"))
            ctrl.goto([],30)
        elif self.command=="Status":
            print("Status")
            if ctrl:
                payload ={"bat":ctrl.vehicle.battery.__str__(),
                "gps":ctrl.vehicle.gps_0.__str__(),
                "alt":ctrl.altitude.__str__()}
            else:    
                payload = {"GPS":"Test","Bat":200}
    

 
 
    def run(self):
        payload = {}
        if self.command=="Launch":
            print("Launchig procedure comand received")
            ctrl.connect()
            thread.start_new_thread(ctrl.launch,())
            pass
        elif self.command=="GoTo":
            print(dt.get("data"))
            ctrl.goto([52.516783, 13.323896],30)
        elif self.command=="Status":
            print("Status")
            if ctrl:
                payload ={"bat":ctrl.vehicle.battery.__str__(),
                "gps":ctrl.vehicle.gps_0.__str__(),
                "alt":ctrl.altitude.__str__()}
            else:    
                payload = {"GPS":"Test","Bat":200}
 """

