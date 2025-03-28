import socket
import threading
import struct
from Camera import Camera
import cv2
import numpy as np
from socketHandler import SocketHandler
from DbController import DbController
from queue import Queue
import time

class GUISocketHandler(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="tcp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "GUI Socket"
        self.initDbController()
        
        self.packetQueue = Queue()
        threading.Thread(target=self.processData, daemon=True)
            
    def processData(self):
        while True:
            data = self.packetQueue.get()
            packetSize = int.from_bytes(data[:4], "little")
            header = data[4]
            cmd = header >> 4
            if cmd == 0x00:
                print("getStream")
                robotID = data[5]
                self.manager.sendToESP(data)
                if header == 0x00:
                    targetStatus = 0b00000100
                elif header == 0x01:
                    targetStatus = 0b00000000
                    
                self.manager.getStatus(robotID)
                self.resend(self.manager.sendToESP, data, targetStatus, 5)
                
            elif cmd == 0x02:
                print("setDriveMode")
                self.robotID = data[5]
                self.manager.sendToESP(data)
                if header == 0x20:
                    targetStatus = 0b00000000
                elif header == 0x21:
                    targetStatus = 0b00000010
                    
                self.manager.getStatus(robotID)
                self.resend(self.manager.sendToESP, data, targetStatus, 5)
                
            elif cmd == 0x04:
                print("requestGrant")
                self.dbCon.myCursor.execute(f"Create user 'readonly_user'@'{self.addr[0]}' identified by '0000'")
                self.dbCon.mydb.commit()
                self.dbCon.myCursor.execute(f"GRANT SELECT ON tfdb.* TO 'readonly_user'@'{self.addr[0]}';")
                self.dbCon.mydb.commit()
                self.dbCon.myCursor.execute("FLUSH PRIVILEGES;")
                self.dbCon.mydb.commit()
        
    def initDbController(self):
        self.dbCon = DbController("localhost", "root", "5315", "mysql")
        self.dbCon.connect()
        self.dbCon.setCursor(True)
        self.dbCon.myCursor.execute("DELETE FROM mysql.db WHERE User='readonly_user';")
        self.dbCon.mydb.commit()
        self.dbCon.myCursor.execute("DELETE FROM mysql.user WHERE User='readonly_user';")
        self.dbCon.mydb.commit()
        self.dbCon.myCursor.execute("DELETE FROM mysql.proxies_priv WHERE User='readonly_user';")
        self.dbCon.mydb.commit()
        self.dbCon.myCursor.execute("FLUSH PRIVILEGES;")
            
class ESPSocketHandler(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="tcp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "ESP Socket"
        
    def processData(self):
        while True:
            data = self.packetQueue.get()
            if len(data) < 4:
                continue
            packetSize = int.from_bytes(data[:4], "little")
            header = data[4]
            cmd = header >> 4
            
            if header == 0x51:
                robotID = data[5]
                _type = data[6]
                status = data[7]
                
                if _type == 0x00:
                    self.manager.robotStatus = status
                elif _type == 0x01:
                    self.manager.streamingStatus = status
               
class AIServerSocket(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "AI Server Socket"
        self.frameQueue = Queue()
        self.displayQueue = Queue()
        threading.Thread(target=self.processFrames, daemon=True).start()
        #threading.Thread(target=self.displayFrame, daemon=True).start()
            
    def processData(self):
        prevFrame = -1
        while True:
            data = self.packetQueue.get()
            if len(data) < 4:
                continue
            packetSize = int.from_bytes(data[:4], "little")
            header = data[4]
            cmd = header >> 4 # check left half byte of header
            if cmd == 1: # sendSteam
                robotId = data[5]
                chunks = data[6]
                frameNum = int.from_bytes(data[7:9], "little")
                chunkIdx = data[9]
                chunkData = data[10:]
                
                if prevFrame != frameNum:
                    chunkBuffer = {}
                chunkBuffer[chunkIdx] = chunkData
                
                if len(chunkBuffer.keys()) == chunks:
                    frame_data = b''.join(chunkBuffer[i] for i in sorted(chunkBuffer.keys()))
                    self.frameQueue.put(frame_data)

                prevFrame = frameNum
            elif cmd == 3: # detect
                event = data[6:].decode("utf-8").split('+')[1]
                if header == 0x30:
                    print("POP")
                    self.manager.detectedEvent.remove(event)
                elif header == 0x31:
                    print("ADD")
                    self.manager.detectedEvent.add(event)
                    
                self.manager.sendToGUI(data)
                if len(self.manager.detectedEvent) == 0:
                    targetStatus = 0b00000010
                elif "쓰러짐" in self.manager.detectedEvent or "사고" in self.manager.detectedEvent:
                    targetStatus = 0b00010000
                else:
                    targetStatus = 0b00001000
                data = struct.pack("<IBB", 2, 0x32, targetStatus)
                
                self.manager.sendToESP(data)
                self.manager.getStatus(robotId)
                self.manager.resend(self.manager.sendToESP, data, targetStatus)
                
                
    def processFrames(self):
        start_time = time.time()
        frameNum = 0
        frame_count = 0
        while True:
            frame_data = self.frameQueue.get()
            imgSize = len(frame_data)
            totalSize = imgSize + 10
            chunks = 0; frameNum = 0; i =0
            
            self.manager.sendToGUI(struct.pack(f"<IBBBHB{imgSize}s", totalSize, 0x10, 0x01, chunks, 
                                              frameNum, i, frame_data))
            
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
    
            frame_count += 1
            if time.time() - start_time >= 1:
                print(f"FPS without imshow: {frame_count}")
                frame_count = 0
                start_time = time.time()
            #self.displayQueue.put(frame)
            self.frameQueue.task_done()
            frameNum += 1
                
    def displayFrame(self):
        while True:
            frame = self.displayQueue.get()
            frame = cv2.resize(frame, (640, 480))
            cv2.imshow("Stream", frame)
            cv2.waitKey(1)
            self.displayQueue.task_done()
            
class SocketManager:
    def __init__(self):
        self.guiHandler = None
        self.espHandler = None
        self.aiHanlder = None
        self.detectedEvent = set()
        self.robotStatus = 0b00000000
        
    def setHandlers(self, guiHandler, espHandler, aiHandler):
        self.guiHandler = guiHandler
        self.espHandler = espHandler
        self.aiHanlder = aiHandler
        
    def sendToESP(self, data):
        if self.espHandler:
            self.espHandler.send(data)

    def sendToGUI(self, data):
        if self.guiHandler:
            self.guiHandler.send(data)
            
    def sendToAIServer(self, data, server=None):
        if self.aiHanlder:
            self.guiHandler.send(data)  
            
    def getStatus(self, robotID):
        header = 0x50
        self.sendToESP(struct.pack("<IBB", 2, header, robotID))
        
    def resend(self, command, data, targetStatus, maxAttempts= 5):
        attempts = [0]
        def checkAndResend():
            
            comparedStatus = self.robotStatus & targetStatus
            if attempts[0] >= maxAttempts or comparedStatus == targetStatus:
                return
            else:
                attempts[0] += 1
                command(data)
                threading.Timer(1, checkAndResend).start()
                
        checkAndResend()