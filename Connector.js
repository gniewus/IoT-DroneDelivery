const ipc = require('node-ipc');
const os = require('os');


ipc.config.id = os.hostname();
ipc.config.id = 'ConnectorIPC';
ipc.config.retry= 1500;

const pythonServer ={
    address : '127.0.0.1',
    port    : 5005
};

ipc.serveNet(
    5006, //we set the port here because the server is already using the default of 5005.
    'udp4',
    function(){
        ipc.server.on(
            'message',
            function(data){
                ipc.log('got a message from ', data);
                if(data.loc){
                    let locString =data.loc.split(":")[1];
                    let locArray = locString.split(",")
                    let latLongAlt = locArray.map((e)=>{
                        return e.split("=")[1]
                    })
                
                    var dist = getDistanceFromLatLonInMeters(52.516783, 13.323896,latLongAlt[0],latLongAlt[1])
                    console.log("Distance form target "+dist)
                    if(dist < 10){
                        ipc.server.emit(pythonServer,'Land',{id:"NodeClient",message:{}})
                    }
                }
            }
        );
    }
);



ipc.server.start(function (params) {
    console.log(params)
});
ipc.server.on("start",()=>{
   ipc.server.emit(pythonServer,'Launch',{id:"NodeClient",message:{}})
    //ipc.server.emit(pythonServer,'GoTo',{id:"NodeClient",alt:30,latlong:[52.516783, 13.323896]})
})

setTimeout(function (params) {
    ipc.server.emit(pythonServer,'GoTo',{id:"NodeClient",alt:30,latlong:[52.516783, 13.323896]})

},25000)

setInterval(function (params) {
    ipc.server.emit(pythonServer,'Status',{id:"NodeClient",message:{}})

},10000)



function getDistanceFromLatLonInMeters(lat1,lon1,lat2,lon2) {
    var R = 6371000; // Radius of the earth in m
    var dLat = deg2rad(lat2-lat1);  // deg2rad below
    var dLon = deg2rad(lon2-lon1); 
    var a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
      Math.sin(dLon/2) * Math.sin(dLon/2)
      ; 
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    var d = R * c; // Distance in m
    return d;
  }
  
  function deg2rad(deg) {
    return deg * (Math.PI/180)
  }
//let server = ipc.connectTo(HOST,PORT,'udp4');




