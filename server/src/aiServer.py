import socket
import threading
import struct
import cv2
import numpy as np
from socketHandler import SocketHandler
from queue import Queue
import time
from ultralytics import YOLO
import mediapipe as mp
from concurrent.futures import ThreadPoolExecutor

class SocketManager:
    def __init__(self):
        self.mainServerHandler = None
        self.espHandler = None
        
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.displayQueue = Queue()
        
        self.detectedEvent = set()
        self.detectedTime
        
    def setHandlers(self, mainServerHandler, espHandler):
        self.mainServerHandler = mainServerHandler
        self.espHandler = espHandler
        
    def sendToESP(self, data):
        if self.espHandler:
            threading.Thread(target=self.espHandler.send, args=(data, ), daemon=True).start()
            
    def sendToMainServer(self, data):
        if self.mainServerHandler:
            threading.Thread(target=self.mainServerHandler.send, args=(data, ), daemon=True).start()
            
    def predictEvent(self, img):
        imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(imgrgb)
        newImg = img.copy()
        if results.pose_landmarks:
            # 키포인트 그리기 (선택적)
            self.mp_drawing.draw_landmarks(newImg, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            
            # 키포인트 추출
            landmarks = results.pose_landmarks.landmark
            shoulderXY = [(int(landmarks[i].x * img.shape[1]), int(landmarks[i].y * img.shape[0])) 
                          for i in [11, 12] if landmarks[i].visibility > 0.5]  # Left/Right Shoulder
            hipXY = [(int(landmarks[i].x * img.shape[1]), int(landmarks[i].y * img.shape[0])) 
                     for i in [23, 24] if landmarks[i].visibility > 0.5]  # Left/Right Hip
            
            if len(shoulderXY) < 1 or len(hipXY) < 1:
                print("Not enough points")
                return newImg
                
            shoulderMid = np.mean(shoulderXY, axis=0).astype(int)
            hipMid = np.mean(hipXY, axis=0).astype(int)
            slope = abs((shoulderMid[1] - hipMid[1]) / (shoulderMid[0] - hipMid[0] + 1e-6))
            cv2.line(newImg, tuple(shoulderMid), tuple(hipMid), (255, 0, 0), 2)
            if slope < 0.5:
                print("Lying")
                durationTime = time.time() - self.detectedTime
                if durationTime >= 5:
                    pass
            else:
                print("Standing")
        else:
            self.detectedTime = time.time()
        return newImg
    
    def displayFrame(self):
        frame = self.displayQueue.get()
        frame = self.predictEvent(frame)
        cv2.imshow("Stream", frame)
        cv2.waitKey(1)
        self.displayQueue.task_done()
   
class ESPSocketHandler(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "ESPSocket"

        self.frameQueue = Queue()
        
        threading.Thread(target=self.processFrames, daemon=True).start()
        
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
                #print(packetSize)
                if prevFrame != frameNum:
                    chunkBuffer = {}
                chunkBuffer[chunkIdx] = chunkData
                
                if len(chunkBuffer.keys()) == chunks:
                    frame_data = b''.join(chunkBuffer[i] for i in sorted(chunkBuffer.keys()))
                    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                    self.frameQueue.put(frame_data)

                prevFrame = frameNum

            except Exception as e:
                print(f"Error: {e}")
                break
            
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
                
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            self.manager.displayQueue.put(frame)
            frame_count += 1
            if time.time() - start_time >= 1:
                print(f"FPS without imshow: {frame_count}")
                frame_count = 0
                start_time = time.time()
            
            self.frameQueue.task_done()
            frameNum += 1             
            
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
