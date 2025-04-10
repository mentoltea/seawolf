from common import *
from eventhandler import *
# import socket
# import time

LOCAL_INFO = socket.gethostbyname_ex(socket.gethostname())

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
        self.thread = None
        
    def __del__(self):
        self.stop()
        self.sock.close()
        
    def send(self, message, host, port):
        if isinstance(message, str):
            message = message.encode('utf-8')
        self.sock.sendto(message, (host, port))
        
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
        def loop():
            nonlocal elapsed
            while not self.stopflag:
                if (elapsed >= timeout): break
                self.sock.sendto(message, (host, self.port))
                time.sleep(timestep)
                elapsed += timestep
            self.stopflag = False
            self.runningflag = False
        self.thread = task.ThreadTask(loop)()
        
    
    def recv(self, timeout=1, buffsize = 4096):
        self.sock.settimeout(timeout)
        try:
            data, addr = self.sock.recvfrom(buffsize)
            return (data, addr)
        except socket.timeout:
            return None
    
    def stop(self):
        self.stopflag = True        
        self.thread = None


EXPECTED_HOSTS = []
class TCP_Sock:
    def __init__(self, host, port, is_server=False):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.connected = False
        self.stopflag = False
        self.is_server = is_server
        if is_server:
            self.sock.bind((host, port))
            self.sock.listen(5)
        else:
            self.sock.connect((host,port))
            
    def __del__(self):
        self.sock.close()

    def stop(self):
        self.stopflag = True
        if self.conn:
            self.conn.close()
            self.conn = None
        
    def accept(self):
        if not self.is_server:
            return
        while not self.connected and not self.stopflag:
            conn, address = self.sock.accept()
            if (address[0] not in EXPECTED_HOSTS):
                conn.close()
                EventHandler.connection_rejected(address[0])
                continue
            self.connected = True
            self.conn = conn
            # self.address = address
            EventHandler.connection_accepted(address[0])
            
        if (self.stopflag):
            self.stopflag = False
    
    def send(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        target = self.conn if self.is_server and self.conn else self.sock
        
        try:
            target.sendall(message)
        except (ConnectionError, AttributeError) as e:
            print(f"Send failed: {e}")
            self.stop()
    
    def recv(self, timeout=1, buffsize=4096):
        target = self.conn if self.is_server and self.conn else self.sock
        if not target:
            return None
            
        target.settimeout(timeout)
        try:
            data = target.recv(buffsize)
            return data
        except socket.timeout:
            return None
        except ConnectionError:
            self.stop()
            return None