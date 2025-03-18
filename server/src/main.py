from server import Server
import threading

def serverThread():
    server = Server("192.168.0.8", 8080)
    server.startServer()
    
def main():
    serverThreadInstance = threading.Thread(target=serverThread(), daemon=True)
    serverThreadInstance.start()
    
if __name__ == "__main__":
    main()