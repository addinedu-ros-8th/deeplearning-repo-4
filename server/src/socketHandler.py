import socket
import threading
from queue import Queue

class SocketHandler:
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="tcp", manager=None):
        self.mode = mode
        self.host = host
        self.port = port
        if type == "tcp":
            self.type = socket.SOCK_STREAM
        elif type == "udp":
            self.type = socket.SOCK_DGRAM
        self.manager = manager
        self.socketName = "Socket"
    
    def reconnect(self):
        self.listen()
    
    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        
    def listen(self):
        if self.mode == "server":
            self.server = socket.socket(socket.AF_INET, self.type)
            self.server.bind((self.host, self.port))
            if self.type == socket.SOCK_STREAM:
                self.server.listen(5)
                print(f"{self.socketName} is connecting..")
                self.client, self.addr = self.server.accept()
                print(f"{self.socketName} is connected : {self.addr}")
        elif self.mode == "client":
            self.client = socket.socket(socket.AF_INET, self.type)
            if self.type == socket.SOCK_STREAM:
                print(f"{self.socketName} is connecting..")
                while True:
                    try:
                        self.client.connect((self.host, self.port))
                        print(f"{self.socketName} is connected")
                        break
                    except ConnectionRefusedError as e:
                        continue
        
        if self.mode == "server" or self.type == socket.SOCK_STREAM:
            self.packetQueue = Queue()
            threading.Thread(target=self.processData, daemon=True).start()
            print("Start listening")
            while True:
                try:
                    if self.type == socket.SOCK_STREAM:
                        data = self.client.recv(65535)
                    else:
                        data, addr = self.server.recvfrom(65535)
                    if not data and self.type == socket.SOCK_STREAM:
                        print(f"{self.socketName} is disconnected")
                        print("Reconnecting..")
                        self.reconnect()
                        
                    self.packetQueue.put(data)
                    
                except Exception as e:
                    print(f"Error: {e}")
                    if self.type == socket.SOCK_STREAM:
                        self.client.close()
                    break
        
    def send(self, data):
        try:
            if self.client:
                if self.type == socket.SOCK_STREAM:
                    self.client.send(data)
                elif self.type == socket.SOCK_DGRAM:
                    self.client.sendto(data, (self.host, self.port))
        except Exception as e:
            print(f"Error : {e}")