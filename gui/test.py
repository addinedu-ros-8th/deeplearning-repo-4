from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt5.QtWidgets import QApplication
import sys
import mysql.connector

class Main:
    def __init__(self):
        self.local = mysql.connector.connect(
            host="192.168.0.180",
            user="root",
            password="5315",
            database="tfdb"
        )

        set0 = QBarSet("기본작업")  # WID 1
        set1 = QBarSet("용접작업")  # WID 2
        set2 = QBarSet("절삭작업")  # WID 3
        set3 = QBarSet("사다리작업")  # WID 4

        # Count the data by work part
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
        # self.chart.setTitle("Debug: Work Violation Stats")

        # Add axes
        categories = ["Q1"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        self.chart.setAxisX(axisX, series)

        axisY = QValueAxis()
        axisY.setRange(0, 10)  # Adjust this range based on your data
        self.chart.setAxisY(axisY, series)

        # Create view for debugging
        self.chart_view = QChartView(self.chart)
        self.chart_view.setMinimumSize(800, 600)
        self.chart_view.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_instance = Main()
    sys.exit(app.exec_())