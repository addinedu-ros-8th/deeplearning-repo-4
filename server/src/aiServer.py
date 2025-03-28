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
        
        # Pose model
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mpDrawing = mp.solutions.drawing_utils
        
        self.fireDetection = YOLO("/home/tm/dev_ws/yolo/runs/detect/fire_detection/weights/fire_detection.pt").to("cuda")
        
        self.displayQueue = Queue()
        
        self.detectedEvent = set()
        self.detectedTime = None
        
        self.bboxQueue = Queue()
        
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
        detectedFires = self.fireDetection.predict(img, conf=0.7)
        
        newImg = img.copy()
        if results.pose_landmarks:
            self.mpDrawing.draw_landmarks(newImg, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            
            landmarks = results.pose_landmarks.landmark
            
            # Draw box on person
            h, w, _ = img.shape
            xCoords = [landmark.x * w for landmark in landmarks]
            yCoords = [landmark.y * h for landmark in landmarks]
            xMin, xMax = int(min(xCoords)), int(max(xCoords))
            yMin, yMax = int(min(yCoords)), int(max(yCoords))
            
            padding = 20
            xMin = max(0, xMin - padding)
            yMin = max(0, yMin - padding)
            xMax = min(w, xMax + padding)
            yMax = min(h, yMax + padding)
            
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
            
            try:
                if slope < 0.3:
                    cv2.rectangle(newImg, (xMin, yMin), (xMax, yMax), (0, 255, 255), 2)
                    durationTime = time.time() - self.detectedTime
                    print(durationTime)
                    if durationTime >= 5:
                        self.sendDetectCommand(0x31, 1, "사고", "쓰러짐")
                        
            except Exception:
                if self.detectedTime == None:
                    self.detectedTime = time.time()
        else:
            self.detectedTime = time.time()
            self.sendDetectCommand(0x30, 1, "사고", "쓰러짐")
            
        for result in detectedFires:
            if len(result.boxes) == 0:
                self.sendDetectCommand(0x30, 1, "사고", "화재")
                break
            xyxy = result.boxes.xyxy
            cv2.rectangle(newImg, (int(xyxy[0][0]), int(xyxy[0][1])), (int(xyxy[0][2]), int(xyxy[0][3])), (0, 0, 255), 2)
            self.sendDetectCommand(0x31, 1, "사고", "화재")
            
        return newImg
    
    def sendDetectCommand(self, header, robotID, typeName, event):
        if event in self.detectedEvent:
            if header == 0x30:
                self.detectedEvent.remove(event)
            elif header == 0x31:
                return
        else:
            if header == 0x30:
                return
            if header == 0x31:
                self.detectedEvent.add(event)
        joinedEvent = typeName + "+" + event
        joinedEvent = joinedEvent.encode("utf-8")
        print("sendDetect")
        dataToSend = struct.pack(f"<IBB{len(joinedEvent)}s", len(joinedEvent) + 2, header, robotID, joinedEvent)
        print(dataToSend)
        self.sendToMainServer(dataToSend)
            
    def displayFrame(self):
        frame = self.displayQueue.get()
        frame = self.predictEvent(frame)
        #cv2.imshow("Stream", frame)
        #cv2.waitKey(1)
        self.displayQueue.task_done()
   
class ESPSocketHandler(SocketHandler):
    def __init__(self, mode="server", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "ESPSocket"

        self.frameQueue = Queue()
        threading.Thread(target=self.processFrames, daemon=True).start()
        
    def processData(self):
        chunkBuffer = {}
        prevFrame = -1
        while True:
            data = self.packetQueue.get()
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
