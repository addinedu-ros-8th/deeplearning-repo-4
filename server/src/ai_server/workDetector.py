from ultralytics import YOLO
import mediapipe as mp
import numpy as np
import cv2
import torch
import os
from config.setting import *

class WorkDetector:
    def __init__(self):
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mpDrawing = mp.solutions.drawing_utils
        device = "cuda" if torch.cuda.is_available() else "cpu"
        baseDir = os.path.dirname(__file__)
        modelPath = os.path.join(baseDir, "fire_detection.pt")
        self.fireDetection = YOLO(modelPath).to(device)
        self.workModel = YOLO("../../deep_learning/data/weights/seven_class_segmentation.pt").to(device)
        self.helmetModel = YOLO("../../deep_learning/data/weights/last_helmet_detection.pt").to(device)
        
    def isHelmetDetected(self, helmetResults):
        if len(helmetResults[0].boxes) > 0:
            names = [helmetResults[0].names[cls.item()] for cls in helmetResults[0].boxes.cls.int()]
            if Label.헬멧 in names:
                return True
        else:
            return False
        
    def isFallenPersonDetected(self, img, poseResults):
        if poseResults.pose_landmarks:
            #self.mpDrawing.draw_landmarks(newImg, poseResults.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
            
            landmarks = poseResults.pose_landmarks.landmark
            
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
            
            if len(shoulderXY) > 0 and len(hipXY) > 0:             
                shoulderMid = np.mean(shoulderXY, axis=0).astype(int)
                hipMid = np.mean(hipXY, axis=0).astype(int)
                slope = abs((shoulderMid[1] - hipMid[1]) / (shoulderMid[0] - hipMid[0] + 1e-6))
                
                if slope < 0.3:
                    return True
                
            return False
        else:
            return False
        
    def isFireDetected(self, fireResults):
        if (len(fireResults[0].boxes)) > 0:
            return True
        else:
            return False
        
    def isWorkDetected(self, workResults):
        if workResults[0].masks is not None:
            return True
        else:
            return False
        
    def getDetectedClasses(self, workResults):
        return [workResults[0].names[int(cls)] for cls in workResults[0].boxes.cls]
    
    def getWorkerMasks(self, workResults):
        masks = workResults[0].masks.xy
        detectedClasses = self.getDetectedClasses(workResults)
        return [masks[i] for i, cls in enumerate(detectedClasses) if cls == Label.작업자]
    
    def getMasks(self, workResults):
        return workResults[0].masks.xy
    
    def isWorkerDetected(self, detectedClasses):
        return Label.작업자 in detectedClasses
    
    def isLadderDetected(self, detectedClasses):
        return Label.사다리 in detectedClasses
    
    def isWeldingDetected(self, masks, detectedClasses, width):
        if Label.용접기 not in detectedClasses:
            return False
        x,y, w, _ = self.getBox(masks, detectedClasses, Label.용접기)
        return self.isCenter(width, x + w//2)
    
    def isFireExtinguisherDetected(self, detectedClasses):
        return Label.소화기 in detectedClasses
    
    def isWeldingmaskDetected(self, detectedClasses):
        return Label.용접가면 in detectedClasses
    
    def isCuttingDetected(self, masks, detectedClasses, width):
        if Label.원형톱 not in detectedClasses:
            return False
        x, y, w, _ = self.getBox(masks, detectedClasses, Label.원형톱)
        return self.isCenter(width, x + w//2)
    
    def isSparkDepenseDetected(self, detectedClasses):
        return Label.불티산방지막 in detectedClasses
    
    def isLadderWorkViolation(self, ladderPolygon, workerMasks):
        _, ladderY, _, ladderH = cv2.boundingRect(ladderPolygon)
        isLadderViolation = False
        for worker in workerMasks:
            workerPolygon = np.array(worker, np.int32)
            x, workerY, _, workerH = cv2.boundingRect(workerPolygon)
            if workerY + workerH - ladderY < ladderH * 0.4:
                isLadderViolation = True
                break
        return isLadderViolation
    
    def getBox(self, masks, detectedClasses, name):
        idx = detectedClasses.index(name)
        polygon = np.array(masks[idx], np.int32)
        return cv2.boundingRect(polygon)
    
    def isCenter(self, width, x):
        ratio = 0.1
        boundary = (width // 2 - width * 0.1, width // 2 + width * 0.1)
        return x >= boundary[0] and x <= boundary[1]
    
        