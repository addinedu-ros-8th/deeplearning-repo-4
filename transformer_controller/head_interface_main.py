from headInterface import *
from motorController import MotorController
import serial
import queue
from led import LED
import os

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
    #ser = serial.Serial("/dev/ttyACM0", 115200, timeout=2)
    threading.Thread(target=aiSocket.streaming, daemon=True).start()
    robotStatus = 0b00000000 # bit 5, 4
    robotLock = threading.Lock()
    time.sleep(2)
    
    led = LED(23)
    delay = 1
    def blink():
        while True:
            with robotLock:
                status = robotStatus
            if (status >> 3) & 0b11 != 0:
                led.on()
                time.sleep(delay)
                led.off()
                time.sleep(delay)
            else:
                time.sleep(0.2)
    threading.Thread(target=blink, daemon=True).start()
    while True:
        try:
            data = manager.mainThreadQueue.get(timeout=0.1)
            if data:
                if len(data) < 4:
                    continue
                header = data[4]
                cmd = header >> 4
                if cmd == 2:
                    targetStatus = data[6]
                    drivingBit = (targetStatus & 0b00000010) >> 1
                    buzzerBit = (targetStatus & 0b00011000) >> 3
                    if drivingBit == 0:
                        drivingStatus = "STOP"
                    else:
                        drivingStatus = "DRIVING"
                    if buzzerBit == 0b00:
                        buzzerStatus = "Clear"
                    elif buzzerBit == 0b01:
                        buzzerStatus = "VIOLATION"
                        delay = 1
                    else:
                        buzzerStatus = "ACCIDENT"
                        delay = 0.5
                    os.system("clear")
                    print("Robot Status: ", drivingStatus)
                    print("Situdation: ", buzzerStatus)
                    
                    with robotLock:
                        robotStatus = targetStatus
                    # ser.write(struct.pack("<IBBB", 3, 0x20, 1, targetStatus))
                    # receivedData = ser.readall()
                    # if len(receivedData) >= 4 and receivedData[4] == 0x51:
                    #     drivingRobotStatus = receivedData[6]
                    #     currentRobotStatus = drivingRobotStatus | robotStatus
                    #     print(bin(currentRobotStatus))
                    #     manager.sendToMainServer(struct.pack("<IBBB", 3, 0x51, 1, currentRobotStatus))

        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            led.clean()
        
if __name__ == "__main__":
    main()
    