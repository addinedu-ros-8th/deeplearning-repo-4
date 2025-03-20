import serial
import struct
import socket


HOST = '192.168.0.6'
PORT = 8080

class Client():
    def __init__(self, HOST="0.0.0.0", PORT=8080):
        self.HOST = HOST
        self.PORT = PORT
    
    def startClient(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.HOST, self.PORT))
        while True:
            n = input()
            if n == 'q':
                break
            self.clientSocket.sendall(n.encode())
        self.clientSocket.close()


def main():
    client = Client(HOST, PORT)
    client.startClient()


if __name__ == "__main__":
    main()
