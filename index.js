var net = require('net');
var fs = require('fs');
var path = require('path');
var socketAdress = "./example.sock";
let currentStatus = {};


var express = require('express');
var exphbs = require('express-handlebars')
var app = express();
var port = 3000;

app.engine('.hbs', exphbs({
    defaultLayout: 'main',
    extname: '.hbs',
    layoutsDir: path.join(__dirname, 'views')
}))
app.set('view engine', '.hbs')
app.set('views', path.join(__dirname, 'views'))


app.get('/', (request, response) => {
    response.render('home', {
        name: 'Tomasz',
        script:'./libs/gmaps.js'
    })
})

app.get('/stats', (request, response) => {
    response.json({
        status: currentStatus
    })
})

app.listen(port, (err) => {
    if (err) {
        return console.log('something bad happened', err)
    }
    console.log(`web server is listening on ${port}`)
})

//Start Server
var server = net.createServer(client => {
    const chunks = [];
    console.log(`client connected`);
    client.setEncoding('utf8');

    client.on('end', () => {
        console.log('client disconnected');
    });

    client.on('data', chunk => {
        console.log(`Got data: ${chunk}`);
        chunks.push(chunk)
        currentStatus = JSON.parse(chunk);
        if (chunk.match(/\r\n$/)) {
            const {ping} = JSON.parse(chunks.join(''));
            client.write(JSON.stringify({pong: ping}));
        }
    });
});


fs.unlink(socketAdress, (err) => {
    if (err) {
        console.log("failed to socket file:" + err);
    } else {
        server.on('listening', () => {
            console.log(`Unix Socket server listening`);
        });
        
        server.listen(socketAdress);
                
        console.log('successfully deleted socket file');
    }
});

