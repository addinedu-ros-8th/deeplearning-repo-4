import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QDataStream, QIODevice
import cv2
import numpy as np

HOST = '192.168.0.180'  # ESP server IP
PORT = 8080            # ESP server port

class TcpClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initSocket()

    def initUI(self):
        # UI 설정 (only cameraLabel)
        self.setWindowTitle("ESP Camera Stream")
        self.resize(640, 480)

        # Set up cameraLabel
        self.cameraLabel = QLabel(self)
        self.cameraLabel.setGeometry(0, 0, 640, 480)  # Adjust size as needed
        self.cameraLabel.setScaledContents(True)      # Scale pixmap to label size

    def initSocket(self):
        # 소켓 초기화
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.onConnected)
        self.socket.readyRead.connect(self.readMessage)
        self.socket.errorOccurred.connect(self.onError)

        # Automatically connect to server on startup
        self.connectToServer()

    def connectToServer(self):
        # 서버에 연결 (ESP server)
        self.socket.connectToHost(HOST, PORT)
        print(f"Connecting to {HOST}:{PORT}...")  # Debug output to console

    def onConnected(self):
        print("Connected to ESP server!")
        # Send initial command (if required by your ESP server)

    def readMessage(self):
        # 서버로부터 이미지 데이터 수신
        while self.socket.bytesAvailable() > 0:
            # Assuming each frame is prefixed with a 4-byte length
            if self.socket.bytesAvailable() >= 4:
                data = self.socket.readAll()
                totalSize = int.from_bytes(data[:4], "little")
                
                header = int.from_bytes(data[4], "little")
                cmd = header >> 4
                if cmd == 1:
                    robotId = data[5]
                    imgData = data[10:]
                    img = np.frombuffer(imgData, np.uint8)
                    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                    self.displayImage(imgData)
                    
                        #return
                # elif cmd == 3:
                #     robotId = data[5]
                #     event = data[4:]
                #     if self.event_callback:
                #         self.event_callback(event)
            else:
                # Not enough data for size; wait for more
                return

    def displayImage(self, frame_data):
        # JPEG 데이터를 QPixmap으로 변환하여 cameraLabel에 표시
        try:
            # Decode JPEG data
            img = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                # Convert BGR to RGB for Qt
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                qimage = QImage(img.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                self.cameraLabel.setPixmap(pixmap)
            else:
                print("Failed to decode image")
        except Exception as e:
            print(f"Image display error: {e}")

    def onError(self):
        # 에러 처리
        error = self.socket.errorString()
        print(f"Error occurred: {error}")

    def closeEvent(self, event):
        # Cleanup on window close
        self.socket.disconnectFromHost()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TcpClient()
    client.show()
    sys.exit(app.exec_())