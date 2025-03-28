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
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QDataStream, QIODevice
import pyqtgraph as pg


HOST = '192.168.0.180'
PORT = 8080

interface = uic.loadUiType("./interface.ui")[0]


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

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


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class ChartCreator:
    def __init__(self):
        self.work_types = {
            1: "기본작업",
            2: "용접작업",
            3: "절삭작업",
            4: "사다리작업",
            5: "사고"
        }
        self.equip_types = {
            1: "안전모",
            2: "용접가면",
            3: "소화기",
            4: "불티산방지막",
            5: "적재물",
            6: "최상단 밑단"
        }
        

    def byWork (self, page, data_dict, query_field, chart_widget):
        """Generic method to create bar charts"""
        # Create bar sets dynamically
        bar_sets = [QBarSet(name) for name in data_dict.values()]
        
        # Fetch data
        cur = self.local.cursor()
        ids = list(data_dict.keys())
        query = f"""
            SELECT r.{query_field}, COUNT(*) AS count 
            FROM Report r 
            WHERE r.{query_field} IN ({','.join(map(str, ids))}) 
            GROUP BY r.{query_field} 
            ORDER BY r.{query_field};
        """
        cur.execute(query)
        results = cur.fetchall()

        # Initialize counts
        counts = {id: 0 for id in ids}
        for result in results:
            id, count = result
            counts[id] = count

        # Fill bar sets with data
        for bar_set, id in zip(bar_sets, ids):
            bar_set.append(counts[id])

        # Create and configure chart
        series = QBarSeries()
        for bar_set in bar_sets:
            series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignBottom)

        # Configure axes

        axisX = QBarCategoryAxis()
        axisX.append([""])
        chart.setAxisX(axisX, series)
       

        axisY = QValueAxis()
        chart.setAxisY(axisY, series)

        # Set up chart view and layout
        chart_view = QChartView(chart)
        layout = QVBoxLayout(page)
        layout.addWidget(chart_view)
        chart_widget.setLayout(layout)

        return chart

    def byEquip(self, page, data_dict, query_field, chart_widget):
        bar_sets = [QBarSet(name) for name in data_dict.values()]
        
        # Fetch data
        cur = self.local.cursor()
        ids = list(data_dict.keys())
        query = f"""
            SELECT s.{query_field}, COUNT(*) AS count 
            FROM Report r
            JOIN SafeCase s ON r.SID = s.SID 
            WHERE s.{query_field} IN ({','.join(map(str, ids))}) 
            GROUP BY s.{query_field} 
            ORDER BY s.{query_field};
        """

        cur.execute(query)
        results = cur.fetchall()
        
        counts = {id: 0 for id in ids}
        for result in results:
            id, count = result
            counts[id] = count

        # Fill bar sets with data
        for bar_set, id in zip(bar_sets, ids):
            bar_set.append(counts[id])

        # Create and configure chart
        series = QBarSeries()
        for bar_set in bar_sets:
            series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignBottom)


        axisX = QBarCategoryAxis()
        axisX.append([""])
        chart.setAxisX(axisX, series)

        axisY = QValueAxis()
        chart.setAxisY(axisY, series)
        
        chart_view = QChartView(chart)
        layout = QVBoxLayout(page)
        layout.addWidget(chart_view)
        chart_widget.setLayout(layout)
        
        return chart


    def statWorkPart(self):
        """Create work part statistics chart"""
        page = self.stackedWidget.widget(1)
        return self.byWork(page, self.work_types, "TID", self.workChart)

    def statEquip(self):
        """Create equipment statistics chart"""
        page = self.stackedWidget.widget(2)
        return self.byEquip(page, self.equip_types, "EID", self.equipChart)



'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class  Interface(QMainWindow, interface):
    image_signal = pyqtSignal(np.ndarray)  # Signal for image updates
    event_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.local = mysql.connector.connect(
            host = "192.168.0.180",
            user = "root",
            password="5315",
            database='tfdb'
        )

        #self.initUI()
        self.initSocket()

        #bonobono
        self.pixmap = QPixmap()
        self.pixmap.load("./bono.png")
        self.pixmap = self.pixmap.scaled(QSize(300,200), Qt.KeepAspectRatioByExpanding)
        self.bono.setPixmap(self.pixmap)
        self.bono.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        

        #connect each button to stackedWidget page
        self.btn1.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btn4.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.btn5.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))
        self.btn6.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(5))
    
        #panel box
        self.box_gray.setStyleSheet("QLabel { border: 2px solid gray; background-color: #dedfdf;}")
        self.box_red.setStyleSheet("QLabel { border: 2px solid red; background-color: #ff9999;}")
        self.box_green.setStyleSheet("QLabel { border: 2px solid green; background-color: #85e085;}")


        #chart and graph
        self.chart_creator = ChartCreator()
        self.chart_creator.local = self.local  # Database connection
        self.chart_creator.stackedWidget = self.stackedWidget
        self.chart_creator.workChart = self.workChart
        self.chart_creator.equipChart = self.equipChart
        self.setup_charts()

        #page 4,5,6
        self.statDaily()
        self.safetyRule()
        self.showData() 




    def initSocket(self):
        # 소켓 초기화
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.onConnected)
        self.socket.readyRead.connect(self.readMessage)
        self.socket.errorOccurred.connect(self.onError)

    def connectToServer(self):
        # 서버에 연결 (ESP server)
        self.socket.connectToHost(HOST, PORT)
        print(f"Connecting to {HOST}:{PORT}...")  # Debug output to console

    def onConnected(self):
        print("Connected to ESP server!")

    def readMessage(self):
        # 서버로부터 이미지 데이터 수신
        while self.socket.bytesAvailable() > 0:
            if self.socket.bytesAvailable() >= 4:
                data = self.socket.readAll()
                totalSize = int.from_bytes(data[:4], "little")
                header = int.from_bytes(data[4], "little")
                cmd = header >> 4
                if cmd == 1:
                    robotId = data[5]
                    imgData = data[10:]
                    img = np.frombuffer(imgData, np.uint8)
                    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                    self.updateCamera(img)
                    
                elif cmd == 3:
                    robotId = data[5]
                    event = data[4:4+totalSize]
                    self.updatePanel(event)
            else:
                # Not enough data for size; wait for more
                return

    def onError(self):
        # 에러 처리
        error = self.socket.errorString()
        print(f"Error occurred: {error}")

    def closeEvent(self, event):
        # Cleanup on window close
        self.socket.disconnectFromHost()
        event.accept()
    


    def setup_charts(self):
        self.chart_creator.statWorkPart()
        self.chart_creator.statEquip()
        # Automatically connect to server on startup
        self.connectToServer()

    

    
    def emitImage(self, image):
        self.image_signal.emit(image)  # Emit image to main thread

    def emitEvent(self, event):
        self.event_signal.emit(event)

    ''' update camera to stream '''
    def updateCamera(self, image):
        try:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception:
            return
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.cameraLabel.width(), self.cameraLabel.height())

        self.cameraLabel.setPixmap(self.pixmap)




    def statDaily(self):
        cur = self.local.cursor()
        query = """
                SELECT DATE(r.Date) AS violation_date, COUNT(*) AS violation_count
                FROM Report r
                GROUP BY DATE(r.Date)
                ORDER BY violation_date ASC
        """
        cur.execute(query)
        results = cur.fetchall()

        series = QLineSeries()
        series.setName("Daily Reports")

        
        for result in results:
            violation_date, violation_count = result
            # Convert the date to a QDateTime object
            date = QDateTime.fromString(str(violation_date), "yyyy-MM-dd")
            # QLineSeries expects x-axis as milliseconds since epoch
            x = date.toMSecsSinceEpoch()
            y = violation_count
            series.append(x, y)

        # Create the chart and add the series
        chart = QChart()
        chart.addSeries(series)
        chart.legend().hide()

        # Configure the x-axis (dates)
        axisX = QDateTimeAxis()
        axisX.setTickCount(8)  # Adjust based on your data range
        axisX.setFormat("MM-dd")  # Date format for labels
        axisX.setTitleText("Date")
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)
        

        axisY = QValueAxis()
        axisY.setLabelFormat("%i")  # Integer format for counts  
        axisY.setRange(0, max(y for _, y in results)) 
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        series.setPen(QPen(QColor("#09DB7F"), 2))  # Blue line, 2px thick
        series.setPointsVisible(True)

        # Create the chart view and add it to page4
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)  # Smooth rendering

        # Add the chart to page4's layout
        layout = QVBoxLayout(self.stackedWidget.widget(3))
        layout.addWidget(chart_view)
        self.dailyChart.setLayout(layout)



    def safetyRule(self):
        self.rule1.setStyleSheet("QLabel { border: 2px solid #F88378; background-color: #F88378; color:black;}")
        self.rule2.setStyleSheet("QLabel { border: 2px solid #FBCEB1; background-color: #FBCEB1; color:black;}")
        self.rule3.setStyleSheet("QLabel { border: 2px solid #AFD9AE; background-color: #AFD9AE; color:black;}")
        self.rule4.setStyleSheet("QLabel { border: 2px solid #43B3AE; background-color: #43B3AE; color:black;}")
        self.rule1.setText("기본작업: 안전모")
        self.rule2.setText("용접작업: 용접가면, 소화기")
        self.rule3.setText("절삭작업: 안전모, 소화기, 불티산방지막")
        self.rule4.setText("사다리작업: 최상단 밑 작업, 사다리 적재물 위 미설치")


    
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
            cur.close()  
    
    ''' update report log from database '''
    def showData(self):
        self.table.setRowCount(0)

        cursor = self.local.cursor()
        cursor.execute("SELECT * FROM Report ORDER BY date DESC")
        results = cursor.fetchall()

        for row in results:
            rowIndex = self.table.rowCount()
            self.table.insertRow(rowIndex)

            # Convert IDs to names
            type_name = self.convertIDtoName("EventType", str(row[2])) 
            equip_name = self.convertIDtoName("SafeCase", str(row[3]))  
            equip_name = self.convertIDtoName("Equipment", equip_name)
            accident_name = self.convertIDtoName("Accident", str(row[4]))  

            # Insert data into columns
            self.table.setItem(rowIndex, 0, QTableWidgetItem(type_name))  # Type
            self.table.setItem(rowIndex, 1, QTableWidgetItem(equip_name))  # Equipment
            self.table.setItem(rowIndex, 2, QTableWidgetItem(accident_name))  # Accident
            self.table.setItem(rowIndex, 3, QTableWidgetItem(str(row[5])))  # Img Path
            self.table.setItem(rowIndex, 4, QTableWidgetItem(str(row[6])))  # Date

    


    ''' update grey, geen, red warning pannel '''
    def updatePanel(self, event):
        DT = int.from_bytes(event[0], "little") & 0x0F
        print(event[2:])
        parts = bytes(event[2:].data()).decode().split('+')
        parts = [part.strip() for part in parts]  # strip space

        typeName, red = parts
        

        if DT == 1:
            self.box_gray.setText(typeName)
            self.box_red.setText(red)
            if red == "쓰러짐" or red == "화재":
                msg = QMessageBox(self)
                msg.setWindowTitle('Danger')
                msg.setText(f'{red} 발생')
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setModal(False)  
                msg.show()  
        
        if DT == 0:
            self.box_gray.setText("Well Done! All Clear :>")
            self.box_green.setText("")
            self.box_red.setText("") 
     


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Interface()
    myWindows.show()
    

    sys.exit(app.exec_())