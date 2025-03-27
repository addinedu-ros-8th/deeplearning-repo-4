import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import time
import cv2, imutils
import urllib.request
import threading
import struct
import socket
from threading import Thread
import numpy as np
import mysql.connector
from datetime import datetime, timedelta
from PyQt5.QtChart import *


HOST = '192.168.0.180'
PORT = 8080

interface = uic.loadUiType("./interface.ui")[0]

class Client():
    def __init__(self, HOST="0.0.0.0", PORT=8080, callback=None):
        self.HOST = HOST
        self.PORT = PORT
        self.callback = callback

    
    def startClient(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((self.HOST, self.PORT))
        cameraThread = Camera(self.clientSocket)
        cameraThread.start()
        dataToSend = struct.pack("<Ib", 1, 0x40)
        self.clientSocket.send(dataToSend)
        
        buffer = b""
        chunk = 25000
        while True : # main or manual is open 
            self.stream = None
            data = self.clientSocket.recv(chunk)
            if data is None:
                break
            imgSize = int.from_bytes(data[:4], "big")
            header = data[4]
            cmd = header >> 4
            if cmd == 1:
                robotId = data[5]
                imgData = data[10:]
                
                img = np.fromstring(imgData, np.int8)
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                if self.callback:
                    self.callback(img)
            
        self.clientSocket.close()
        
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class Camera(Thread):
    def __init__(self, clientSocket, parent = None):
        super().__init__()
        self.main = parent
        self.clientSocket = clientSocket
        self.running = False

    def run(self):
        while self.running:
            self.clientSocket.send(b"SM\n")

    def stop(self):
        self.running = False

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class  Interface(QMainWindow, interface):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.local = mysql.connector.connect(
            host = "192.168.0.180",
            user = "root",
            password="5315",
            database='tfdb'
        )

        #bonobono
        self.pixmap = QPixmap()
        self.pixmap.load("./bono.png")
        self.pixmap = self.pixmap.scaled(QSize(200,200), Qt.KeepAspectRatioByExpanding)
        self.safetyRight.setPixmap(self.pixmap)
        self.safetyRight.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        

        #send command
        self.client = Client(HOST, PORT, callback = self.updateCamera)
        threading.Thread(target=self.client.startClient, daemon=True).start()

        #camera
        self.isCameraOn = False
        self.cameraBox = Camera(self)
        self.cameraBox.start()
        #self.btn_camera.clicked.connect(self.controlCamera)

        # connect each button to stackedWidget page
        self.btn1.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn4.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.btn5.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))
        self.btn6.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(5))

        #page-chart
        #self.stackedWidget.addWidget(self.page2) 
        self.statWorkPart()

        #self.stackedWidget.setCurrentIndex(1)

        #show log
        self.showData() 
        self.updateRed()
        #self.updateGreen()
        #self.updateGray

        #panel box
        self.box_gray.setStyleSheet("QLabel { border: 2px solid gray; background-color: #dedfdf;}")
        self.box_red.setStyleSheet("QLabel { border: 2px solid red; background-color: #ff9999;}")
        self.box_green.setStyleSheet("QLabel { border: 2px solid green; background-color: #85e085;}")

    
    ''' send command to server '''
    def sendCommand(self):
        client = Client(HOST, PORT)
        client.startClient()

    
    ''' update camera to stream '''
    def updateCamera(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.cameraLabel.width(), self.cameraLabel.height())

        self.cameraLabel.setPixmap(self.pixmap)

    ''' create chart (작업별 위반통계) '''
    def statWorkPart (self):    
        self.page2 = self.stackedWidget.widget(1)  # Ensure it matches page index
        set0 = QBarSet("기본작업")
        set1 = QBarSet("용접작업")
        set2 = QBarSet("절삭작업")
        set3 = QBarSet("사다리작업")

        # count the data by work part
        cur = self.local.cursor()
        query = "SELECT s.WID, COUNT(*) AS wid_count FROM Report r JOIN SafeCase s ON r.SID = s.SID WHERE s.WID IN (1, 2, 3, 4) GROUP BY s.WID ORDER BY s.WID;"
        cur.execute(query)
        results = cur.fetchall()

        # Initialize counts to 0 in case some WIDs have no data
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for result in results:
            wid = result[0]  # WID value (1, 2, 3, or 4)
            count = result[1]  # Count for that WID
            counts[wid] = count

        # Add data to the bar sets
        set0.append(counts[1])
        set1.append(counts[2])
        set2.append(counts[3])
        set3.append(counts[4])

        # Create series
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        series.append(set2)
        series.append(set3)

        # Create chart
        self.chart = QChart()
        self.chart.addSeries(series)
        #self.chart.setTitle("Debug: Work Violation Stats")

        # Add axes
        categories = ["Q1"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        self.chart.setAxisX(axisX, series)

        axisY = QValueAxis()
        #axisY.setRange(0, 10)
        self.chart.setAxisY(axisY, series)

        self.chart_view = QChartView(self.chart)
        
        # ✅ Place Chart in Page 2
        layout = QVBoxLayout(self.page2)  # Use Page 2
        layout.addWidget(self.chart_view)
        self.workChart.setLayout(layout)
    

    def statEquip(self):
        self.page3 = self.stackedWidget.widget(2)  # Ensure it matches page index
        set0 = QBarSet("안전모")
        set1 = QBarSet("용접가면")
        set2 = QBarSet("소화기")
        set3 = QBarSet("불티산방지막")
        set4 = QBarSet("적재물")
        set5 = QBarSet("화재")
        set6 = QBarSet("쓰러짐")

        # count the data by work part
        cur = self.local.cursor()
        query = "SELECT s.EID, COUNT(*) AS eid_count FROM Report r JOIN SafeCase s ON r.SID = s.SID WHERE s.EID IN (1, 2, 3, 4, 5, 6, 7) GROUP BY s.EID ORDER BY s.EID;"
        cur.execute(query)
        results = cur.fetchall()

        # Initialize counts to 0 in case some WIDs have no data
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        for result in results:
            eid = result[0]  
            count = result[1]  # Count for that EID
            counts[eid] = count

        # Add data to the bar sets
        set0.append(counts[1])
        set1.append(counts[2])
        set2.append(counts[3])
        set3.append(counts[4])
        set4.append(counts[5])
        set5.append(counts[6])
        set6.append(counts[7])

        # Create series
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        series.append(set2)
        series.append(set3)
        series.append(set4)
        series.append(set5)
        series.append(set6)

        # Create chart
        self.chart = QChart()
        self.chart.addSeries(series)
        #self.chart.setTitle("Debug: Work Violation Stats")

        # Add axes
        categories = ["Q1"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        self.chart.setAxisX(axisX, series)

        axisY = QValueAxis()
        #axisY.setRange(0, 10)
        self.chart.setAxisY(axisY, series)

        self.chart_view = QChartView(self.chart)
        
        # ✅ Place Chart in Page 2
        layout = QVBoxLayout(self.page3)  # Use Page 3
        layout.addWidget(self.chart_view)
        self.workChart.setLayout(layout)
    

    
    ''' conver ID (int) to Name (string) '''
    def convertIDtoName(self, table, id):
        map = {
            "EventType": ["TID", "typeName"],
            "SafeCase": ["SID", "EID"],
            "Equipment": ["EID", "equipName"],
            "Accident": ["AID", "accidentName"],
            "WorkPart": ["WID", "workName"]
        }
        try:
            cur = self.local.cursor()
            # Select 'name' column instead of the ID column
            query = f"SELECT {map[table][1]} FROM {table} WHERE {map[table][0]} = {id}"
            cur.execute(query)  # Use parameterized query
            result = cur.fetchone()
            return result[0] if result else "Unknown"  # Return name or "Unknown" if no match
        except mysql.connector.Error as e:
            print(f"Error in convertIDtoName: {e}")
            return None
        finally:
            cur.close()  # Always close the cursor

    
    ''' update report log from database '''
    def showData(self):
        self.table.setRowCount(0)

        cursor = self.local.cursor()
        cursor.execute("SELECT * FROM Report")
        results = cursor.fetchall()

        for row in results:
            rowIndex = self.table.rowCount()
            self.table.insertRow(rowIndex)

            # Convert IDs to names
            type_name = self.convertIDtoName("EventType", str(row[2]))  # TID -> Name
            equip_name = self.convertIDtoName("SafeCase", str(row[3]))  # SID -> Equip Name
            equip_name = self.convertIDtoName("Equipment", equip_name)
            accident_name = self.convertIDtoName("Accident", str(row[4]))  # AID -> Name

            # Insert data into columns
            self.table.setItem(rowIndex, 0, QTableWidgetItem(type_name))  # Type
            self.table.setItem(rowIndex, 1, QTableWidgetItem(equip_name))  # Equipment
            self.table.setItem(rowIndex, 2, QTableWidgetItem(accident_name))  # Accident
            self.table.setItem(rowIndex, 3, QTableWidgetItem(str(row[5])))  # Img Path
            self.table.setItem(rowIndex, 4, QTableWidgetItem(str(row[6])))  # Date

    

    ''' update red warning pannel from database '''
    def updateRed(self):
        

        try:
            cur = self.local.cursor()

            #time_threshold = datetime.now() - timedelta(seconds=20)
            #cur.execute("SELECT * FROM Report WHERE date >= %s", (time_threshold,))
            cur.execute("SELECT SID FROM Report")
            results = cur.fetchall()
            equip_names = []

            for result in results:
                sid = str(result[0])  # Get the SID from each tuple
                
                # Get EID for this SID
                cur.execute("SELECT EID FROM SafeCase WHERE SID = %s", (sid,))
                equipID_result = cur.fetchall()
                
                if equipID_result:  # Check if we got any results
                    equipID = str(equipID_result[0][0])
                    
                    # Get equipment name for this EID
                    cur.execute("SELECT equipName FROM Equipment WHERE EID = %s", (equipID,))
                    equipName = cur.fetchall()
                    
                    if equipName:  # Check if we got an equipment name
                        equip_names.append(str(equipName[0][0]))

            
            # Display all equipment names or "No data found" if the list is empty
            display_text = "\n".join(equip_names) if equip_names else "No Recent Data"
            self.box_red.setText(display_text)

        except mysql.connector.Error as e:
            # Handle database errors
            self.box_red.setText(f"Error: {str(e)}")
        finally:
            # Clean up resources
            if 'cur' in locals():
                cur.close()
            if 'local' in locals() and self.local.is_connected():
                self.local.close()


class Receiver (QThread):
    detected = pyqtSignal(bytes)

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.isRunning = False
    
    def run(self):
        print("recv start")
        self.isRunning = True

        while (self.isRunning == True):
            if self.conn.readable():
                res = self.conn.read_until(b'\n')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Interface()
    myWindows.show()
    

    sys.exit(app.exec_())