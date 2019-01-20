# -*- coding: UTF-8 -*-
import __future__

import socket
import json
import os

server_address = './example.sock'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(server_address)
sock.connect(server_address)

# Listen for incoming connections
msg = json.dumps({"ping": "hello"}).encode('UTF-8')
sock.send(msg)
sock.send(b"\r\n")

data = sock.recv(256)
print(data.decode('UTF-8'))

sock.close()