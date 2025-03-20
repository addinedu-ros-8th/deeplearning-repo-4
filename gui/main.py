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

# from log import Log
# from manual import Manual

HOST = '192.168.0.8'
PORT = 8080

main = uic.loadUiType("./main.ui")[0]
manual= uic.loadUiType("./manual.ui")[0]
log = uic.loadUiType("./log.ui")[0]



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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
        buffer = b""
        chunk = 25000
        while True : # main or manual is open 
            self.stream = None
            data = self.clientSocket.recv(chunk)
            if data is None:
                break
            buffer += data
            while b'\n' in data:
                cmd, data = data.split(b'\n', 1)
                print("Recv: ", cmd)
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
        self.running = True

    def run(self):
        while self.running:
            self.clientSocket.send(b"SM\n")
            time.sleep(0.2)

    def stop(self):
        self.running = False
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class  Main (QMainWindow, main):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pixmap = QPixmap()

        #send command
        self.client = Client(HOST, PORT, callback = self.updateCamera)
        threading.Thread(target=self.client.startClient, daemon=True).start()

        #move the page
        self.btn_manual.clicked.connect(self.openManualMode) 
        self.btn_history.clicked.connect(self.openLog)

        #time update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        self.updateTime()

        #label box
        warningLabel = [self.safetyHat, self.securityChain, self.safetyGlass, self.weldingHelmet, 
                        self.fireFreezer, self.sparkProof, self.fire, self.flammable, 
                        self.fallingDanger, self.load]
        
        for label in warningLabel:
            text = label.text()
            self.isDetected(label, text)
            
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def sendCommand(self):
        client = Client(HOST, PORT)
        client.startClient()

    def openManualMode(self):
        self.manual_window = Manual()
        self.manual_window.show()

    def openLog(self):
        self.log_window = Log()
        self.log_window.show()


    def updateTime(self):
        currentDate = QDateTime.currentDateTime().toString("yyyy - MM - dd  hh:mm:ss")
        self.dateTime.setText(currentDate)
    
    
    def updateCamera(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.cameraBox.width(), self.cameraBox.height())

        self.cameraBox.setPixmap(self.pixmap)


    ''' change the text box of color when it violated '''
    def changeColor(self, box, text):
        box.setStyleSheet("background-color: #CA3433;") #change the color of background
        box.setText(text + " 위반")

        
    ''' return back the text box status when it solved '''
    def solved(self, box, text):
        box.setStyleSheet("background-color: transparent;")
        box.setText(text)
        

    ''' check if it is detected or not '''
    def isDetected(self, box, text):
        command = "" #receive the command & check if it's 0 or 1

        if command == "DT": 
            if "": #  && 1 = is detected something
                self.changeColor(box, text)

            else: #  0 = is not detected
                self.solved(box, text)


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
class Manual(QMainWindow, manual):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class Log (QMainWindow, log):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

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
    myWindows = Main()
    myWindows.show()
    

    sys.exit(app.exec_())

