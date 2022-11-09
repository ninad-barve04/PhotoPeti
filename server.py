import socket
import os

from server_funcs import *

# Socket object for server
ServerSocket = socket.socket()
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = '192.168.0.109'
#host = 'localhost'
port = 8080

try:
    ServerSocket.bind((host, port))
    print("Server started on "+str(host)+":"+str(port))
except socket.error as e:
    print(e)

ServerSocket.listen(5) 
# 5 means server can accept 5 connections at the same time
# So 5 clients can connect and 6th client will have to wait until some connection opens up 


while True:
    Client, address = ServerSocket.accept()
    service_client(Client)
