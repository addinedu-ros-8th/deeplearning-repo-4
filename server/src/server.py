import socket
import threading
import struct
from Camera import Camera
import cv2
import numpy as np

class CommandHandler:
    def __init__(self, clientSocket:socket.socket):
        self.clientSocket = clientSocket
        
    def processData(self, data):
        if data[:2] == b"SM":
            self.processSM()
    
    def processSM(self):
        webcam = Camera(cv2.VideoCapture(0))
        img = webcam.getImg()
        if img is None:
            print("No image")
            return
        
        ret, buffer = cv2.imencode(".jpg", img)
        imgData = buffer.tobytes()
        imgDataLength = len(imgData)
        
        dataToSend = struct.pack(f"<2sI{imgDataLength}s", b"SM", imgDataLength, imgData)
        print("Send: ", imgDataLength)
        self.clientSocket.send(dataToSend)
        
class Server():
    def __init__(self, HOST="0.0.0.0", PORT=8080):
        self.HOST = HOST
        self.PORT = PORT
        
    def handleClient(self, clientSocket):
        cmdHandler = CommandHandler(clientSocket)
        buffer = b""
        while True:
            try:
                if self.isClientDisconnected(clientSocket):
                    print(f"{clientSocket} is Disconnected.")
                    break
                data = clientSocket.recv(1024)

                buffer += data
                
                while b'\n' in data:
                    cmd, buffer = data.split(b'\n', 1)
                    print(f"Received: {cmd}")
                    cmdHandler.processData(cmd)                
                
            except Exception as e:
                print(f"Error: {e}")
                clientSocket.close()
                break
    def isClientDisconnected(self, clientSocket):
        try:
            data = clientSocket.recv(1024, socket.MSG_PEEK)
            return len(data) == 0
        except socket.error:
            return True
    
    def startServer(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.HOST, self.PORT))
        self.serverSocket.listen(5)
        print(f"Server is waiting at {self.HOST}:{self.PORT}..")
        
        while True:
            clientSocket, clientAddress = self.serverSocket.accept()
            print(f"{clientAddress} is connected.")
            
            clientHandler = threading.Thread(target = self.handleClient, args = (clientSocket, ))
            clientHandler.start()
            
    def processData(data):
        pass
        
