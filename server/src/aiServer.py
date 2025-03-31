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
from workDetector import WorkDetector

class SocketManager:
    def __init__(self):
        self.mainServerHandler = None
        self.espHandler = None
        self.workDetector = WorkDetector()
        
        self.displayQueue = Queue()
        
        self.detectedEvent = set()
        self.detectedTime = None
        
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
        poseResults = self.workDetector.pose.process(imgrgb)
        fireResults = self.workDetector.fireDetection.predict(img, conf=0.7, verbose=False)
        workResults = self.workDetector.workModel.predict(img, conf=0.5, verbose=False)
        helmetResults = self.workDetector.helmetModel.predict(img, verbose=False, conf=0.5)
        
        newImg = img.copy()
        
        # Fallen person detected        
        if self.workDetector.isFallenPersonDetected(img, poseResults):
            if self.detectedTime is None:
                self.detectedTime = time.time()
            else:
                durationTime = time.time() - self.detectedTime
                print(durationTime)
                if durationTime >= 5:
                    self.sendDetectCommand(0x31, 1, "사고", "쓰러짐")
                        
        else:
            self.detectedTime = None
            self.sendDetectCommand(0x30, 1, "사고", "쓰러짐")
        
        # Fire detected    
        if self.workDetector.isFireDetected(fireResults):
            self.sendDetectCommand(0x31, 1, "사고", "화재")
            for box in fireResults[0].boxes:
                xyxy = box.xyxy
                cv2.rectangle(newImg, (int(xyxy[0][0]), int(xyxy[0][1])), (int(xyxy[0][2]), int(xyxy[0][3])), (0, 0, 255), 2)
        else:
            self.sendDetectCommand(0x30, 1, "사고", "화재")
        
        if self.workDetector.isWorkDetected(workResults):
            masks = self.workDetector.getMasks(workResults)
            detectedClasses = self.workDetector.getDetectedClasses(workResults)
            # Ladder detected
            if self.workDetector.isLadderDetected(detectedClasses):
                # Worker detected
                if self.workDetector.isWorkerDetected(detectedClasses):
                    helmetResults = self.workDetector.helmetModel.predict(img, verbose=False, conf=0.5)
                    # Helmet deteceted
                    if self.workDetector.isHelmetDetected(helmetResults):
                        self.sendDetectCommand(0x30, 1, "사다리 작업 위반", "안전모")
                    else:
                        self.sendDetectCommand(0x31, 1, "사다리 작업 위반", "안전모")
                    ladderIdx = detectedClasses.index("WO-03")
                    ladderPolygon = masks[ladderIdx]
                    workerMasks = self.workDetector.getWorkerMasks(workResults)
                    # Ladder work violation detected
                    if self.workDetector.isLadderWorkViolation(ladderPolygon, workerMasks):
                        self.sendDetectCommand(0x31, 1, "사다리 작업 위반", "최상단 밑단 작업")
                    else:
                        self.sendDetectCommand(0x30, 1, "사다리 작업 위반", "최상단 밑단 작업")
            else:
                self.sendDetectCommand(0x30, 1, "사다리 작업 위반")
            
            # Welding detected                    
            if self.workDetector.isWeldingDetected(detectedClasses):
                # Welding mask detected
                if self.workDetector.isWeldingmaskDetected(detectedClasses):
                    self.sendDetectCommand(0x30, 1, "용접 작업 위반", "용접가면")
                else:
                    self.sendDetectCommand(0x31, 1, "용접 작업 위반", "용접가면")
                # Fire distinguisher detected
                if self.workDetector.isFireExtinguisherDetected(detectedClasses):
                    self.sendDetectCommand(0x30, 1, "용접 작업 위반", "소화기")
                else:
                    self.sendDetectCommand(0x31, 1, "용접 작업 위반", "소화기")
            else:
                self.sendDetectCommand(0x30, 1, "용접 작업 위반")
            # Cutting detected 
            if self.workDetector.isCuttingDetected(detectedClasses):
                # Spark depense detected
                if self.workDetector.isSparkDepenseDetected(detectedClasses):
                    self.sendDetectCommand(0x30, 1, "절삭 작업 위반", "불티산방지막")
                else:
                    self.sendDetectCommand(0x31, 1, "절삭 작업 위반", "불티산방지막")
                # Fire distinguisher detected
                if self.workDetector.isFireExtinguisherDetected(detectedClasses):
                    self.sendDetectCommand(0x30, 1, "절삭 작업 위반", "소화기")
                else:
                    self.sendDetectCommand(0x31, 1, "절삭 작업 위반", "소화기")
                # Helmet detected
                if self.workDetector.isHelmetDetected(helmetResults):
                    self.sendDetectCommand(0x30, 1, "절삭 작업 위반", "안전모")
                else:
                    self.sendDetectCommand(0x31, 1, "절삭 작업 위반", "안전모")
            else:
                self.sendDetectCommand(0x30, 1, "절삭 작업 위반")
            # Worker detected
            if self.workDetector.isWorkerDetected(detectedClasses):
                # Helmet detected
                if self.workDetector.isHelmetDetected(helmetResults):
                    self.sendDetectCommand(0x30, 1, "장비 위반", "안전모")
                else:
                    self.sendDetectCommand(0x31, 1, "장비 위반", "안전모")
            else:
                self.sendDetectCommand(0x30, 1, "장비 위반")
                    
            for idx, mask in enumerate(masks):
                # 다각형 좌표를 numpy 배열로 변환
                polygon = np.array(mask, np.int32)
                
                # 바운딩 박스 계산
                x, y, w, h = cv2.boundingRect(polygon)
                cv2.putText(newImg, detectedClasses[idx], (x, y), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 2)
                
                # 이미지에 바운딩 박스 그리기
                cv2.rectangle(newImg, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색 박스
        
        return newImg
    
    def sendDetectCommand(self, header, robotID, typeName, event=None):
        if event is not None:
            joinedEvent = typeName + "+" + event
            if joinedEvent in self.detectedEvent:
                if header == 0x30:
                    self.detectedEvent.remove(joinedEvent)
                else:
                    return
            else:
                if header == 0x31:
                    self.detectedEvent.add(joinedEvent)
                else:
                    return
        else:
            joinedEvent = typeName
            copyEvent = self.detectedEvent.copy()
            hasEvent = False
            for each in copyEvent:
                if joinedEvent in each:
                    self.detectedEvent.remove(each)
                    hasEvent = True
                if hasEvent == False:
                    return
        joinedEvent = joinedEvent.encode("utf-8")
        
        print("sendDetect")
        dataToSend = struct.pack(f"<IBB{len(joinedEvent)}s", len(joinedEvent) + 2, header, robotID, joinedEvent)
        print(dataToSend)
        self.sendToMainServer(dataToSend)
            
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
