from headInterface import *

aiHost = "192.168.0.180"
mainHost = "192.168.0.180"
mainPort = 8082
aiPort = 8083
def main():
    manager = SocketManager()
    mainSocket = MainServerSocketHandler("client", mainHost, 8081, "tcp", manager)
    aiSocket = AISocketHandler("client", aiHost, aiPort, "udp", manager)
    manager.setHandlers(mainSocket, aiSocket)
    mainSocket.start()
    aiSocket.start()
    
    while True:
        aiSocket.streaming()
        pass
if __name__ == "__main__":
    main()
    