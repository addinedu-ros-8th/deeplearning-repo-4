from main_server import *
from config.setting import *

host = "192.168.0.180"
guiPort = 8080
visionPort = 8081
aiPort = 8082

def main():
    manager = SocketManager()
    guiSocket = GUISocketHandler("server", SocketIP.MAIN_SERVER_IP, SocketPort.MAIN_GUI_PORT, "tcp", manager)
    visionSocket = VisionSocketHandler("server", SocketIP.MAIN_SERVER_IP, SocketPort.MAIN_VISION_PORT, "tcp", manager)
    aiSocket = AIServerSocket("server", SocketIP.MAIN_SERVER_IP, SocketPort.MAIN_AI_PORT, "udp", manager)
    manager.setHandlers(guiSocket, visionSocket, aiSocket)
    guiSocket.start()
    aiSocket.start()
    visionSocket.start()
    while True:
        pass
if __name__ == "__main__":
    main()