import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QDataStream, QIODevice
import cv2
import numpy as np
import mysql.connector

HOST = '192.168.0.180'  # ESP server IP
PORT = 8080            # ESP server port

class TcpClient(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setupUi(self)
        self.local = mysql.connector.connect(
            host = "192.168.0.180",
            user = "root",
            password="5315",
            database='tfdb'
        )

        self.checkSafety("절삭작업 위반", ["소화기", "불티산방지막"])


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

    def checkSafety(self, typeName, red):  
        cursor = self.local.cursor()
        cursor.execute("SELECT * FROM SafeCase")
        results = cursor.fetchall()

        
        # Build the safe_case_map: EventType name -> list of Equipment names
        safe_case_map = {}
        for row in results:
            sid, wid, eid = row  # Unpack (SID, WID, EID)
            event_type_name = self.convertIDtoName("EventType", wid)
            equipment_name = self.convertIDtoName("Equipment", eid)
            if event_type_name not in safe_case_map:
                safe_case_map[event_type_name] = []  # Initialize list for this event type
            safe_case_map[event_type_name].append(equipment_name)  # Append equipment name
        
        print(safe_case_map)

        # Check for typeName and update box_green with safe equipment
        for key in safe_case_map:
            if typeName == key:
                # Find equipment not in the 'red' list (safe equipment)
                safe_equipment = [eq for eq in safe_case_map[key] if eq not in red]
                # Convert to string for setText
                print(", ".join(safe_equipment) if safe_equipment else "All safe")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TcpClient()
    client.show()
    sys.exit(app.exec_())