const ipc = require('node-ipc');
const os = require('os');
var argv = require('minimist')(process.argv.slice(2));
const pythonServer = {
    address: '127.0.0.1',
    port: 5005
};

//console.dir(argv);


ipc.config.id = 'ConnectorIPC';
ipc.config.retry = 1500;
ipc.config.silent = true;
//Flag to confirm that the package was
let buttonClicked = false;
let landed = false;
let comingHome = false;
const TEL = [52.512904, 13.322384];
const MAR = [52.5167824, 13.3238021];
ipc.serveNet(
    5006, //we set the port here because the server is already using the default of 5005.
    'udp4',
    function () {
        ipc.server.on(
            'message',
            function (data) {
                if (data.loc) {
                    let locString = data.loc.split(":")[1];
                    let locArray = locString.split(",")
                    let latLongAlt = locArray.map((e) => {
                        return e.split("=")[1]
                    })
                    let bat = data.bat.split("=");
                    console.log([latLongAlt], data.groundspeed.slice(3) + " m/s", bat[bat.length - 1], data.mode)
                }
                if (data.Operation) {
                    console.log(data);
                    handleResponse(data);


                }
            }
        );
    }
);

async function handleResponse(data) {

    if (data.Operation == "GoTo" && data.Status == "Success") {
        ipc.server.emit(pythonServer, 'Land', {id: "NodeClient", message: {}})


    } else if (data.Operation == "Land" && data.Status == "Success") {
        landed = true;
        if (comingHome) {
            ipc.server.emit(pythonServer, 'MissionComplete', {id: "NodeClient", message: {}})
        } else {
            timeout(ipc.server.emit(pythonServer, 'Launch', {id: "NodeClient", message: {}}), 3000);
            timeout(ipc.server.emit(pythonServer, 'TakeOff', {id: "NodeClient", message: {}}), 8000);
        }

    } else if (data.Operation == "TakeOff" && data.Status == "Success") {
        var targetLoc = MAR;
        if (landed == true) {
            targetLoc = TEL;
            comingHome = true;
        }

        ipc.server.emit(pythonServer, 'GoTo', {
            id: "NodeClient",
            alt: 30,
            latlong: targetLoc,
        })

    }

}

ipc.server.start();

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

ipc.server.on("start", async function () {
    ipc.server.emit(pythonServer, 'Launch', {id: "NodeClient", message: {}})
    await timeout(ipc.server.emit(pythonServer, 'TakeOff', {alt: "", id: "NodeClient", message: {}}), 2500)
})

function getDistanceFromLatLonInMeters(lat1, lon1, lat2, lon2) {
    var R = 6371000; // Radius of the earth in m
    var dLat = deg2rad(lat2 - lat1);  // deg2rad below
    var dLon = deg2rad(lon2 - lon1);

    function deg2rad(deg) {
        return deg * (Math.PI / 180)
    }

    var a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
    ;
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    var d = R * c; // Distance in m
    return d;


}


//let server = ipc.connectTo(HOST,PORT,'udp4');




