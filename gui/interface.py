import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import time
import cv2, imutils
import urllib.request
import threading
import struct
import socket
from threading import Thread
import numpy as np
import mysql.connector


HOST = '192.168.0.180'
PORT = 8080

interface = uic.loadUiType("./interface.ui")[0]

class Client():
    def __init__(self, HOST="0.0.0.0", PORT=8080, callback=None):
        self.HOST = HOST
        self.PORT = PORT
        self.callback = callback
    
    def startClient(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.HOST, self.PORT))
        cameraThread = Camera(self.clientSocket)
        cameraThread.start()
        dataToSend = struct.pack("<Ib", 1, 0x40)
        self.clientSocket.send(dataToSend)
        
        buffer = b""
        chunk = 25000
        while True : # main or manual is open 
            self.stream = None
            data = self.clientSocket.recv(chunk)
            if data is None:
                break
            imgSize = int.from_bytes(data[:4], "big")
            header = data[4]
            cmd = header >> 4
            if cmd == 1:
                robotId = data[5]
                imgData = data[10:]
                
                img = np.fromstring(imgData, np.int8)
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                if self.callback:
                    self.callback(img)
            
        self.clientSocket.close()
        
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class Camera(Thread):
    def __init__(self, clientSocket, parent = None):
        super().__init__()
        self.main = parent
        self.clientSocket = clientSocket
        self.running = False

    def run(self):
        while self.running:
            self.clientSocket.send(b"SM\n")

    def stop(self):
        self.running = False

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class  Interface(QMainWindow, interface):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pixmap = QPixmap()

        #send command
        self.client = Client(HOST, PORT, callback = self.updateCamera)
        threading.Thread(target=self.client.startClient, daemon=True).start()

        #camera
        self.isCameraOn = False
        self.cameraBox = Camera(self)
        self.cameraBox.start()
        #self.btn_camera.clicked.connect(self.controlCamera)


        #panel box
        self.box_red.setStyleSheet("QLabel { border: 2px solid red; background-color: #ff9999;}")
        self.box_green.setStyleSheet("QLabel { border: 2px solid green; background-color: #85e085;}")

    
    ''' send command to server '''
    def sendCommand(self):
        client = Client(HOST, PORT)
        client.startClient()

    
    ''' update camera to stream '''
    def updateCamera(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.cameraLabel.width(), self.cameraLabel.height())

        self.cameraLabel.setPixmap(self.pixmap)


class Receiver (QThread):
    detected = pyqtSignal(bytes)

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.isRunning = False
    
    def run(self):
        print("recv start")
        self.isRunning = True

        while (self.isRunning == True):
            if self.conn.readable():
                res = self.conn.read_until(b'\n')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Interface()
    myWindows.show()
    

    sys.exit(app.exec_())