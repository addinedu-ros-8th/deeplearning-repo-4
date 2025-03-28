from mainServer import *
import threading
import socket

host = "192.168.0.180"
guiPort = 8080
espPort = 8081
aiPort = 8082
    
def main():
    manager = SocketManager()
    guiSocket = GUISocketHandler("server", host, guiPort, "tcp", manager)
    espSocket = ESPSocketHandler("server", host, espPort, "tcp", manager)
    aiSocket = AIServerSocket("server", host, aiPort, "udp", manager)
    manager.setHandlers(guiSocket, espSocket, aiSocket)
    guiSocket.start()
    aiSocket.start()
    espSocket.start()
    while True:
        pass
    guiSocket.dbCon.close()
if __name__ == "__main__":
    main()