import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import time
import cv2, imutils
import urllib.request
import threading
import serial
import struct
import socket

# from log import Log
# from manual import Manual

HOST = '192.168.0.6'
PORT = 8080

main = uic.loadUiType("./main.ui")[0]
manual= uic.loadUiType("./manual.ui")[0]
log = uic.loadUiType("./log.ui")[0]



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Client():
    def __init__(self, HOST="0.0.0.0", PORT=8080):
        self.HOST = HOST
        self.PORT = PORT

    
    def startClient(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.HOST, self.PORT))
        while True : # main or manual is open 
            n = "SM\n"
            self.clientSocket.sendall(n.encode())

            data = b""  
            while True:  
                chunk = self.clientSocket.recv(4096)  
                if not chunk:  
                    print("Server closed connection")  
                    return  
                data += chunk  
                if b"\n" in chunk:  
                    break
            print(f"Received {len(data)} bytes:", data[:20])
        
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent = None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        while self.running == True:
            self.update.emit()
            time.sleep(0.048)

    def stop(self):
        self.running = False
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class  Main (QMainWindow, main):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pixmap = QPixmap()

        #send command
        self.client = Client(HOST, PORT)
        threading.Thread(target=self.client.startClient, daemon=True).start()
    
        #camera setting
        self.isCameraOn = True
        self.pixmap = QPixmap()
        self.cameraBox = Camera(self)
        self.cameraBox.daemon = True
        self.cameraBox.update.connect(self.updateCamera)
        
        
        #move the page
        self.btn_manual.clicked.connect(self.openManualMode) 
        self.btn_history.clicked.connect(self.openLog)

        #time update
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_time)
        # self.timer.start(1000)
        # #self.update_time()

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
    
    
    def updateCamera(self):
        retval, image = self.video.read()

        if retval:
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

