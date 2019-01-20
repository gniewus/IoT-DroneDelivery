from unix_socket import UnixSocket
import thread
import time 

#ctrl = DroneController()
#ctrl.connect()
us = UnixSocket()


try:
    us.run_unix_domain_socket_server()
    
    #ctrl.launch()
    #ctrl.goto([52.516783, 13.323896],30)
except Exception as e:
    print("Error: unable to start thread " + e.message)
while 1:
    time.sleep(1)
    # us.sendStats(ctrl._print_stats(True))
    pass
