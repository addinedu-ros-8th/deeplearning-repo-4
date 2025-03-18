import socket
import struct
import cv2
import numpy as np 

HOST = "192.168.0.8"
PORT = 8080

class Client():
    def __init__(self, HOST="0.0.0.0", PORT=8080):
        self.HOST = HOST
        self.PORT = PORT
    
    def startClient(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.HOST, self.PORT))
        print(f"{HOST} is connected")
        self.clientSocket.send(b"SM\n")
        
        buffer = b""
        chunk = 4096
        while True:
            data = self.clientSocket.recv(chunk)
            if data is None:
                break
    
            if data[:2] == b"SM":
                imgDataLength = struct.unpack("<I", data[2:6])[0]
                remainLength = imgDataLength - 4090
                imgData = data[6:chunk]
                while True:
                    if chunk <= remainLength:
                        remainLength -= chunk
                        data = self.clientSocket.recv(chunk)
                        imgData += data
                    else:
                        data = self.clientSocket.recv(remainLength)
                        imgData += data
                        break
                img = np.fromstring(imgData, np.int8)
                
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                cv2.imshow("img", img)
                cv2.waitKey(0.01)
                cv2.destroyAllWindows()
        
        self.clientSocket.close()
        
def main():
    client = Client(HOST, PORT)
    client.startClient()
        
if __name__ == "__main__":
    main()