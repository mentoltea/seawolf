from common import *
from eventhandler import *
# import socket
# import time

ALL_INTERFACES = '0.0.0.0'
ALL_HOSTS = '255.255.255.255'
UDP_BROADCAST_PORT = 6969 # constant

TCP_INCOMING_PORT = UDP_BROADCAST_PORT + 1 # constant

TCP_OUTCOMING_PORT = UDP_BROADCAST_PORT + 2 # depends on host's port

class UDP_Sock:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.runningflag = False
        self.stopflag = False
        
    def __del__(self):
        self.sock.close()
        
    def send(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        self.sock.sendto(message, (self.host, self.port))
        
    def start_sending(self, message, timestep = 1, timeout = float('inf')):
        if self.runningflag:
            return
        self.runningflag = True
        elapsed = 0
        if isinstance(message, str):
            message = message.encode('utf-8')
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        host = self.host
        if host == ALL_INTERFACES:
            host = ALL_HOSTS
        while not self.stopflag:
            if (elapsed >= timeout): break
            self.sock.sendto(message, (host, self.port))
            time.sleep(timestep)
            elapsed += timestep
        self.stopflag = False
    
    def recv(self, timeout=1, buffsize = 4096):
        self.sock.settimeout(timeout)
        try:
            data, addr = self.sock.recvfrom(buffsize)
            return (data, addr)
        except socket.timeout:
            return None
    
    def stop(self):
        self.runningflag = False
        self.stopflag = True        


EXPECTED_HOSTS = []
class TCP_Sock:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.connected = False
    
    def __del__(self):
        self.sock.close()
    
    def listen(self, backlog=5):
        self.sock.listen(backlog)
    
    def accept(self):
        while not self.connected:
            client_socket, client_address = self.sock.accept()
            if (client_address[0] not in EXPECTED_HOSTS):
                client_socket.close()
                EventHandler.connection_rejected(client_address[0])
                continue
            self.connected = True
            self.client_socket = client_socket
            self.client_address = client_address
            EventHandler.connection_accepted(client_address[0])
    
    def connect(self):
        self.sock.connect((self.host, self.port))
    