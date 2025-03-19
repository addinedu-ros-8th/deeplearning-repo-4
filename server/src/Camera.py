import cv2

class Camera:
    def __init__(self, cap):
        self.cap = cap
    
    def getImg(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            
    def getFps(self):
        return cv2.CAP_PROP_FPS