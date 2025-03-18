from server import *
import threading

host = "192.168.219.114"
guiPort = 8080
espPort = 8081
    
def main():
    manager = SocketManager()
    guiSocket = GUISocketHandler(host, guiPort)
    espSocket = ESPSocketHandler(host, espPort)
    manager.setHandlers(guiSocket, espSocket)
    guiSocket.start()
    espSocket.start()
    while True:
        pass
if __name__ == "__main__":
    main()