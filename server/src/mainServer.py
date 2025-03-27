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
        
    def listen(self):
        super().listen()
        while True:
            try:
                data = self.client.recv(4)
                if not data:
                    print(f"{self.socketName} is disconnected")
                    print("Reconnecting..")
                    self.reconnect()
                dataLength = struct.unpack("<I", data)[0]
                header = self.client.recv(1)
                self.processData(header, dataLength)
            except Exception as e:
                print(f"Error: {e}")
                self.client.close()
                break
            
    def processData(self, header, dataLength):
        cmd = struct.unpack("<b", header)[0] >> 4
        if cmd == 0x00:
            print("getStream")
            robotId = self.client.recv(1)
            self.manager.sendToESP(struct.pack("<IBB", 2, header, robotId))
        elif cmd == 0x02:
            print("setDriveMode")
            robotId = self.client.recv(1)
            self.manager.sendToESP(struct.pack("<BB", 2, header, robotId))
        elif cmd == 0x04:
            print("requestGrant")
            self.dbCon.myCursor.execute(f"Create user 'readonly_user'@'{self.addr[0]}' identified by '0000'")
            self.dbCon.mydb.commit()
            self.dbCon.myCursor.execute(f"GRANT SELECT ON tfdb.* TO 'readonly_user'@'{self.addr[0]}';")
            self.dbCon.mydb.commit()
            self.dbCon.myCursor.execute("FLUSH PRIVILEGES;")
            self.dbCon.mydb.commit()
        
        """
        while b'\n' in data:
            cmd, data = data.split(b'\n', 1)
            print("Recv: ", cmd)
            if cmd[:2] == b"SM":
                #self.manager.sendToESP(b"SM\n")
                img = cv2.imread("home/tm/Downloads/20250317180459.jpg")
                ret, imgData = cv2.imencode(".jpg", img)
                self.send(struct.pack(f"<3sI{len(imgData)}s", b"SM\n", len(imgData), imgData))
        """
        
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
    def __init__(self, mode="client", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "ESP Socket"

class AIServerSocket(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "AI Server Socket"
        self.frameQueue = Queue()
        self.displayQueue = Queue()
        self.packetQueue = Queue()
        threading.Thread(target=self.processFrames, daemon=True).start()
        threading.Thread(target=self.displayFrame, daemon=True).start()
        threading.Thread(target=self.processData, daemon=True).start()
        
    def listen(self):
        super().listen()
        
        while True:
            data, addr = self.server.recvfrom(65535)
            
            self.packetQueue.put(data)
            
    def processData(self):
        chunk = 10240
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
                eventData = "안전모 미착용"
                totalSize = len(eventData) + 1
                # self.manager.sendToGUI(struct.pack(f"<IB{len(eventData)}s", totalSize, header, eventData))
                
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
            self.displayQueue.put(frame)
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
        