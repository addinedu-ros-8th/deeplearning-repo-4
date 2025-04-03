import threading
import struct
import cv2
import numpy as np
from socketHandler import SocketHandler
from DbController import DbController
from queue import Queue
import time
import socket

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
            
            if cmd == 0x02:
                print("setDriveMode")
                self.robotID = data[5]
                self.manager.sendToESP(data)
                
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
        
    def listen(self):
        self.server = socket.socket(socket.AF_INET, self.type)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"{self.socketName} is connecting..")
        self.client, self.addr = self.server.accept()
        print(f"{self.socketName} is connected : {self.addr}")
        
    def send(self, data):
        maxRetry = 5
        retry = 0
        if self.client:
            header = data[4]
            if header == 0x20:
                targetStatus = data[6]
                self.client.settimeout(1)
                self.client.send(data)
                    
               
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
                robotID = data[5]
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
            elif cmd == 2:
                self.manager.sendToESP(data)
            elif cmd == 3: # detect
                robotID = data[5]
                event = data[6:]
                parsedEvent = event.decode("utf-8").split('+')

                if header == 0x30:
                    if parsedEvent[0] == "사고":
                        self.manager.detectedEvent.remove(parsedEvent[1])
                elif header == 0x31:
                    if parsedEvent[0] == "사고":
                        self.manager.detectedEvent.add(parsedEvent[1])
                
                data = struct.pack(f"<IBB{len(event)}s", len(event) + 2, header, robotID, event)
                self.manager.sendToGUI(data)
                print(self.manager.detectedEvent)
                if len(self.manager.detectedEvent) > 0:
                    if len(self.manager.detectedEvent) == 1 and next(iter(self.manager.detectedEvent)) == "감지":
                        targetStatus = 0b00000000 # Stop for detecting
                        print("Stop for detecting")
                    else:
                        targetStatus = 0b00010000 # Accident, Stop
                        print("Accident, Stop")
                elif len(event) > 0:
                    targetStatus = 0b00001000 # Violation, Stop
                    print("Violation, Stop")
                else:
                    targetStatus = 0b00000010 # Driving
                    print("Driving")
                
                
                data = struct.pack("<IBBB", 3, 0x20, 1, targetStatus)
                
                threading.Thread(target=self.manager.sendToESP, args=(data,)).start()
                
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
            cv2.waitKey(30)
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
            self.aiHandler.send(data)  
            
    def getStatus(self, robotID):
        header = 0x50
        self.sendToESP(struct.pack("<IBB", 2, header, robotID))
        
