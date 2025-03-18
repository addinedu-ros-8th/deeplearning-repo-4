import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import Qt 

manual = uic.loadUiType("./manual.ui")[0]

class Manual (QMainWindow, manual):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
       

        

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = Manual()
    myWindows.show()

    sys.exit(app.exec_())
