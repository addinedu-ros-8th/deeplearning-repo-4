from aiServer import *
import threading
import cv2

mainServerIp = "192.168.0.180"
mainServerPort = 8082
host = "192.168.0.180"
espPort = 8081

def main():
    manager = SocketManager()
    espSocket = ESPSocketHandler("server", host, espPort, "udp", manager)
    mainServerSocket = MainServerSocketHandler("client", host, mainServerPort, "udp", manager)
    manager.setHandlers(mainServerSocket, espSocket)
    espSocket.start()
    mainServerSocket.start()
    while True:
        pass
if __name__ == "__main__":
    main()