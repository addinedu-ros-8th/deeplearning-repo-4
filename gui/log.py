import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt 

log = uic.loadUiType("log.ui")[0]
main = uic.loadUiType("./main.ui")[0]

class Log (QMainWindow, log):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_home.clicked.connect(self.openHome)

    
    def openHome(self):
        self.main_window = Main()
        self.main_window.show()


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class Main (QMainWindow, main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Log()
    myWindows.show()

    sys.exit(app.exec_())