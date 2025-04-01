from socketHandler import SocketHandler
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import struct
import threading
import time

class AISocketHandler(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "AI Server Socket"
        
        self.picam2 = Picamera2()
        video_config = self.picam2.create_video_configuration(
            main={"size": (320, 240)}, 
            transform=Transform(hflip=True, vflip=True)
        )
        self.picam2.configure(video_config)
        self.picam2.start()
        
    def streaming(self):
        frameNum = 0
        while True:
            frameData = self.picam2.capture_array()
            frameData = cv2.cvtColor(frameData, cv2.COLOR_RGB2BGR)
            ret, frameData = cv2.imencode('.jpg', frameData)
            
            if not ret:
                continue
            frameData = frameData.tobytes()
            
            imgSize = len(frameData)
            chunkSize = 10240
            chunks = (imgSize + chunkSize - 1) // chunkSize
            
            for i in range(chunks):
                offset = i * chunkSize
                imgChunkSize = min(chunkSize, imgSize - offset)
                totalSize = imgChunkSize + 10 
                self.manager.sendToAIServer(struct.pack(f"<IBBBHB{imgChunkSize}s", totalSize, 0x10, 0x01, chunks, frameNum, i,
                                                        frameData[offset:]))
            time.sleep(0.05)
            frameNum += 1
            
            
class MainServerSocketHandler(SocketHandler):
    def __init__(self, mode="client", host="0.0.0.0", port=0, type="tcp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "Main Server Socket"
        
class SocketManager:
    def __init__(self):
        self.aiHanlder = None
        self.mainHandler = None
        
    def setHandlers(self, mainHandler, aiHandler):
        self.mainHandler = mainHandler
        self.aiHandler = aiHandler

    def sendToAIServer(self, data):
        if self.aiHandler:
            self.aiHandler.send(data) 
            
    def sendToMainServer(self, data):
        if self.mainHandler:
            self.mainHandler.send(data) 