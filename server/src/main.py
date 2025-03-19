from server import *
import threading

host = "192.168.0.8"
guiPort = 8080
espPort = 8081
    
def main():
    manager = SocketManager()
    guiSocket = GUISocketHandler(host, guiPort, manager)
    espSocket = ESPSocketHandler(host, espPort, manager)
    manager.setHandlers(guiSocket, espSocket)
    guiSocket.start()
    espSocket.start()
    while True:
        pass
if __name__ == "__main__":
    main()