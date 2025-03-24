import socket
import threading
import struct
import cv2
import numpy as np
from socketHandler import SocketHandler
from queue import Queue
import time

class SocketManager:
    def __init__(self):
        self.mainServerHandler = None
        self.espHandler = None
        
    def setHandlers(self, mainServerHandler, espHandler):
        self.mainServerHandler = mainServerHandler
        self.espHandler = espHandler
        
    def sendToESP(self, data):
        if self.espHandler:
            threading.Thread(target=self.espHandler.send, args=(data, ), daemon=True).start()
            
    def sendToMainServer(self, data):
        if self.mainServerHandler:
            threading.Thread(target=self.mainServerHandler.send, args=(data, ), daemon=True).start()
   
class ESPSocketHandler(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "ESPSocket"
        
        self.frameQueue = Queue()
        self.displayQueue = Queue()
        threading.Thread(target=self.processFrames, daemon=True).start()
        threading.Thread(target=self.displayFrame, daemon=True).start()
        
    def listen(self):
        super().listen()
        print("Start listening!")
        chunkBuffer = {}
        prevFrame = -1
        while True:
            try:
                data, addr = self.server.recvfrom(65535)
                packetSize = int.from_bytes(data[:4], "little")
                header = data[4]
                robotId = data[5]
                chunks = data[6]
                frameNum = int.from_bytes(data[7:9], "little")
                chunkIdx = data[9]
                chunkData = data[10:]
                print(packetSize)
                if prevFrame != frameNum:
                    chunkBuffer = {}
                chunkBuffer[chunkIdx] = chunkData
                
                if len(chunkBuffer.keys()) == chunks:
                    frame_data = b''.join(chunkBuffer[i] for i in sorted(chunkBuffer.keys()))
                    
                    self.frameQueue.put(frame_data)

                prevFrame = frameNum

                
            except Exception as e:
                print(f"Error: {e}")
                break
        
    def processData(self):
        pass
    
    def processFrames(self):
        start_time = time.time()
        frameNum = 0
        frame_count = 0
        while True:
            frame_data = self.frameQueue.get()
            chunk = 10240
            imgSize = len(frame_data)
            chunks = (imgSize + chunk - 1) // chunk
            
            for i in range(chunks):
                offset = i * chunk
                imgChunkSize = min(chunk, imgSize - offset)
                totalSize = imgSize + 10
                
                self.manager.sendToMainServer(struct.pack(f"<IBBBHB{imgSize}s", totalSize, 0x10, 0x01, chunks, 
                                              frameNum, i, frame_data[offset:offset+imgChunkSize]))
                
                
            #frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            #frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            frame_count += 1
            if time.time() - start_time >= 1:
                print(f"FPS without imshow: {frame_count}")
                frame_count = 0
                start_time = time.time()
            
            self.frameQueue.task_done()
            frameNum += 1
                
    def displayFrame(self):
        while True:
            frame = self.displayQueue.get()
            cv2.imshow("Stream", frame)
            cv2.waitKey(1)
            self.displayQueue.task_done()
        
            
class MainServerSocketHandler(SocketHandler):
    def __init__(self, mode="client", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "Main Server Socket"
        
    
    def listen(self):
        super().listen()
    def testSend(self):
        while True:
            self.client.sendto(b"hi", (self.host, self.port))
            print("SEND")
