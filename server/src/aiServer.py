import threading
import struct
import cv2
import numpy as np
from socketHandler import SocketHandler
from queue import Queue
import time
from workDetector import WorkDetector

class SocketManager:
    def __init__(self):
        self.mainServerHandler = None
        self.espHandler = None
        self.workDetector = WorkDetector()
        
        self.displayQueue = Queue()
        
        self.detectedEvent = {}
        self.detectedAccident = set()
        self.fallenDetectedTime = None
        self.fireDetectedTime = None
        
        self.frameChunkSize = 5
        self.idx = 0
        
        self.accident = {}
        self.event = {}
        
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
        height, width, _ = img.shape
        newImg = img.copy()
        
        # Fallen person detected        
        if self.workDetector.isFallenPersonDetected(img, poseResults):
            if self.fallenDetectedTime is None:
                self.fallenDetectedTime = time.time()
            else:
                durationTime = time.time() - self.fallenDetectedTime
                print(durationTime)
                if durationTime >= 5:
                    self.accident["쓰러짐"] = self.accident.get("쓰러짐", 0) + 1
            self.accident["감지"] = self.accident.get("감지", 0) + 1
        else:
            self.fallenDetectedTime = None
        
        # Fire detected    
        if self.workDetector.isFireDetected(fireResults):
            if self.fireDetectedTime is None:
                self.fireDetectedTime = time.time()
            else:
                durationTime = time.time() - self.fireDetectedTime
                print(durationTime)
                if durationTime >= 2:
                    self.accident["화재"] = self.accident.get("화재", 0) + 1
            self.accident["감지"] = self.accident.get("감지", 0) + 1
            for box in fireResults[0].boxes:
                xyxy = box.xyxy
                cv2.rectangle(newImg, (int(xyxy[0][0]), int(xyxy[0][1])), (int(xyxy[0][2]), int(xyxy[0][3])), (0, 0, 255), 2)
        else:
            self.fireDetectedTime = None
        
        if self.workDetector.isWorkDetected(workResults):
            masks = self.workDetector.getMasks(workResults)
            detectedClasses = self.workDetector.getDetectedClasses(workResults)
            
            isOtherWorkDetected = False
            # Ladder detected
            if self.workDetector.isLadderDetected(detectedClasses):
                temp = []
                # Worker detected
                if self.workDetector.isWorkerDetected(detectedClasses):
                    isOtherWorkDetected = True
                    helmetResults = self.workDetector.helmetModel.predict(img, verbose=False, conf=0.5)
                    # Helmet deteceted
                    if not self.workDetector.isHelmetDetected(helmetResults):
                        temp.append("안전모")
            
                    ladderIdx = detectedClasses.index("WO-03")
                    ladderPolygon = masks[ladderIdx]
                    workerMasks = self.workDetector.getWorkerMasks(workResults)
                    # Ladder work violation detected
                    if self.workDetector.isLadderWorkViolation(ladderPolygon, workerMasks):
                        temp.append("최상단 밑단")
                if len(temp) > 0:
                    self.event.setdefault("사다리작업 위반", {})
                    for each in temp:
                        self.event["사다리작업 위반"][each] = self.event["사다리작업 위반"].get(each, 0) + 1
            
            # Welding detected                    
            if self.workDetector.isWeldingDetected(masks, detectedClasses, width):
                temp = []
                # Welding mask detected
                if not self.workDetector.isWeldingmaskDetected(detectedClasses):
                    temp.append("용접가면")
        
                # Fire distinguisher detected
                if not self.workDetector.isFireExtinguisherDetected(detectedClasses):
                    temp.append("소화기")
                    
                if len(temp) > 0:
                    self.event.setdefault("용접작업 위반", {})
                    for each in temp:
                        self.event["용접작업 위반"][each] = self.event["용접작업 위반"].get(each, 0) + 1
            # Cutting detected 
            if self.workDetector.isCuttingDetected(masks, detectedClasses, width):
                temp = []
                isOtherWorkDetected = True
                # Spark depense detected
                if not self.workDetector.isSparkDepenseDetected(detectedClasses):
                    temp.append("불티산방지막")

                # Fire distinguisher detected
                if not self.workDetector.isFireExtinguisherDetected(detectedClasses):
                    temp.append("소화기")

                # Helmet detected
                if not self.workDetector.isHelmetDetected(helmetResults):
                    temp.append("안전모")
                if len(temp) > 0:
                    self.event.setdefault("절삭작업 위반", {})
                    
                    for each in temp:
                        self.event["절삭작업 위반"][each] = self.event["절삭작업 위반"].get(each, 0) + 1
            # Worker detected
            if self.workDetector.isWorkerDetected(detectedClasses) and isOtherWorkDetected == False:
                temp = []
                # Helmet detected
                if not self.workDetector.isHelmetDetected(helmetResults):
                    temp.append("안전모")
                if len(temp) > 0:
                    self.event.setdefault("장비위반", {})
                    for each in temp:
                        self.event["장비위반"][each] = self.event["장비위반"].get(each, 0) + 1
                  
            for idx, mask in enumerate(masks):
                # 다각형 좌표를 numpy 배열로 변환
                polygon = np.array(mask, np.int32)
                
                # 바운딩 박스 계산
                x, y, w, h = cv2.boundingRect(polygon)
                #cv2.putText(newImg, detectedClasses[idx], (x, y), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 2)
                                                                                                                     
                # 이미지에 바운딩 박스 그리기
                cv2.rectangle(newImg, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Yellow box
        cv2.line(newImg, (int(width//2 - width*0.1), 0), (int(width//2 - width*0.1), height), (0, 255, 0), 2)  
        cv2.line(newImg, (int(width//2 + width*0.1), 0), (int(width//2 + width*0.1), height), (0, 255, 0), 2)        
        self.idx = (self.idx + 1) % self.frameChunkSize
        if self.idx == self.frameChunkSize - 1:
            event = {type: [each for each, number in value.items() if number > self.frameChunkSize // 2] for type, value in self.event.items()}
            accident = {type for type in self.accident.keys()}
            if len(accident) > 1:
                accident.remove("감지")
            event = {type: violations for type, violations in event.items() if violations}
            self.event.clear()
            self.accident.clear()       
            self.processEvent(event)
            self.processAccident(accident)
        return newImg
    
    def processEvent(self, eventDic):
        isUpdate = False
        for type, event in eventDic.items():
            if type not in self.detectedEvent:
                isUpdate = True
            else:
                for each in event:
                    if each not in iter(self.detectedEvent[type]):
                        isUpdate = True
        for type, event in self.detectedEvent.items():
            if type not in eventDic:
                isUpdate = True
            else:
                for each in iter(event):
                    if each not in eventDic[type]:
                        isUpdate = True
        if isUpdate:
            self.detectedEvent = eventDic
            eventList = []
            keys = self.detectedEvent.keys()
            for key in keys:
                li = [key] + list(self.detectedEvent[key])
                eventList.append('+'.join(li))
            joinedEvent = '/'.join(eventList)
            self.sendDetectCommand(0x31, 1, event=joinedEvent)
            
    def processAccident(self, accidentSet):
        for each in accidentSet:
            if each not in self.detectedAccident:
                self.sendDetectCommand(0x31, 1, "사고", each)
        for each in self.detectedAccident:
            if each not in accidentSet:
                self.sendDetectCommand(0x30, 1, "사고", each)
        self.detectedAccident = accidentSet
            
    def sendDetectCommand(self, header, robotID, typeName=None, event=None):
        if typeName == None:
            joinedEvent = event
        else:
            joinedEvent = typeName + '+' + event
        print(joinedEvent)
        joinedEvent = joinedEvent.encode("utf-8")
        
        dataToSend = struct.pack(f"<IBB{len(joinedEvent)}s", len(joinedEvent) + 2, header, robotID, joinedEvent)
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
            self.manager.sendToMainServer(data)
            if len(chunkBuffer.keys()) == chunks:
                frame_data = b''.join(chunkBuffer[i] for i in sorted(chunkBuffer.keys()))
                frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                if frameNum % 2 == 0:
                    self.frameQueue.put(frame_data)

            prevFrame = frameNum
            
    def processFrames(self):
        start_time = time.time()
        frame_count = 0
        while True:
            frame_data = self.frameQueue.get()
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            self.manager.displayQueue.put(frame)
            # frame_count += 1
            # if time.time() - start_time >= 1:
            #     print(f"FPS without imshow: {frame_count}")
            #     frame_count = 0
            #     start_time = time.time()
            
            # self.frameQueue.task_done()            
            
class MainServerSocketHandler(SocketHandler):
    def __init__(self, mode="client", host="0.0.0.0", port=0, type="udp", manager=None):
        super().__init__(mode, host, port, type, manager)
        self.socketName = "Main Server Socket"
