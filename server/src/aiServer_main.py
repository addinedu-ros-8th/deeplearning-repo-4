from ai_server import *
from config.setting import *

def main():
    manager = SocketManager()
    visionSocket = VisionSocketHandler("server", SocketIP.AI_SERVER_IP, SocketPort.AI_VISION_PORT, "udp", manager)
    mainServerSocket = MainServerSocketHandler("client", SocketIP.MAIN_SERVER_IP, SocketPort.MAIN_AI_PORT, "udp", manager)
    manager.setHandlers(mainServerSocket, visionSocket)
    visionSocket.start()
    mainServerSocket.start()

    while True:
        manager.displayFrame()
if __name__ == "__main__":
    main()