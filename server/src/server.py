import socket
import threading
import struct
from Camera import Camera
import cv2
import numpy as np

class SocketHandler:
    def __init__(self, host, port, manager=None):
        self.host = host
        self.port = port
        self.manager = manager
        self.socketName = "Socket"
        self.connect()
    
    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
    
    def reconnect(self):
        self.listen()
    
    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        
    def listen(self):
        print(f"{self.socketName} is connecting..")
        self.client, addr = self.server.accept()
        print(f"{self.socketName} is connected : {addr}")
        
    def send(self, data):
        if self.client:
            self.client.send(data)

class GUISocketHandler(SocketHandler):
    def __init__(self, host, port, manager=None):
        super().__init__(host, port, manager)
        self.socketName = "GUI Socket"
        self.webcam = Camera(cv2.VideoCapture(0))
        
    def listen(self):
        print(f"{self.socketName} is connecting..")
        self.client, addr = self.server.accept()
        print(f"{self.socketName} is connected : {addr}")
        buffer = b""
        while True:
            try:
                data = self.client.recv(1024)
                if not data:
                    break
                
                buffer += data
                while b'\n' in buffer:
                    cmd, buffer = data.split(b'\n', 1)
                    print(f"Received: {cmd}")
                    self.processData(cmd)
            except Exception as e:
                print(f"Error: {e}")
                self.client.close()
                break
            
    def processData(self, data):
        if data[:2] == b"SM":
            img = self.webcam.getImg()
            if img is None:
                print("No image")
                return
            ret, buffer = cv2.imencode(".jpg", img)
            imgData = buffer.tobytes()
            imgDataLength = len(imgData)
            
            dataToSend = struct.pack(f"<2sI{imgDataLength}s", b"SM", imgDataLength, imgData)
            print("Send: ", imgDataLength)
            self.send(dataToSend)
            
class ESPSocketHandler(SocketHandler):
    def __init__(self, host, port, manager):
        super().__init__(host, port, manager)
        self.socketName = "ESP Socket"
        
    def listen(self):
        print(f"{self.socketName} is connecting..")
        self.client, addr = self.server.accept()
        print(f"{self.socketName} is connected : {addr}")
        buffer = b""
        while True:
            try:
                data = self.client.recv(1024)
                if not data:
                    print(f"{self.socketName} is disconnected")
                    print("Reconnecting..")
                    self.reconnect()
                buffer += data
                
                buffer = self.processData(buffer)
            except Exception as e:
                print(f"Error: {e}")
                self.client.close()
                break
            
    def processData(self, data):
        while b'\n' in data:
            cmd, data = data.split(b'\n', 1)
            if cmd[:2] == b"SM":
                imgDataLength = struct.unpack("<I", data[:4])[0]
                print(imgDataLength)
                imgData = data[4:]
                data = b""
                imgDataLength -= len(imgData)
                while imgDataLength > 0:
                    cmd = self.client.recv(min(1024, imgDataLength))
                    imgData += cmd
                    imgDataLength -= len(cmd)
                
                img = np.frombuffer(imgData, np.uint8)
                print(len(img))
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                
                cv2.imshow("img", img)
                cv2.waitKey(1)
                
        return data
            
class SocketManager:
    def __init__(self):
        self.guiHandler = None
        self.espHandler = None
        
    def setHandlers(self, guiHandler, espHandler):
        self.guiHandler = guiHandler
        self.espHandler = espHandler
        
    def SendToESP(self, data):
        if self.espHandler:
            self.espHandler.send(data)

    def SendToGUI(self, data):
        if self.guiHandler:
            self.guiHandler.send(data)