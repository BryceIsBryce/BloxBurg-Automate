from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import time

from FastFoodWorker.OrderDetection import ImageRecognitionAI


class Window(QMainWindow):
    def __init__(self, UIFileName: str, parent=None) -> None:
        super(Window, self).__init__(parent=parent)
        uic.loadUi(UIFileName + ".ui", self)

        QApplication.setStyle("Fusion")

        DefaultFont = QApplication.font()
        # DefaultFont.setPointSize(DefaultFont.pointSize() + 2)
        DefaultFont.setPointSize(DefaultFont.pointSize())
        QApplication.setFont(DefaultFont)

        DarkPalette = QPalette()
        DarkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
        DarkPalette.setColor(QPalette.WindowText, Qt.white)
        DarkPalette.setColor(
            QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        DarkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
        DarkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        DarkPalette.setColor(QPalette.ToolTipBase, Qt.white)
        DarkPalette.setColor(QPalette.ToolTipText, Qt.white)
        DarkPalette.setColor(QPalette.Text, Qt.white)
        DarkPalette.setColor(
            QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        DarkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
        DarkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        DarkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
        DarkPalette.setColor(QPalette.ButtonText, Qt.white)
        DarkPalette.setColor(
            QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        DarkPalette.setColor(QPalette.BrightText, Qt.red)
        DarkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
        DarkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        DarkPalette.setColor(
            QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        DarkPalette.setColor(QPalette.HighlightedText, Qt.white)
        DarkPalette.setColor(
            QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

        QApplication.setPalette(DarkPalette)

class Ui(Window):
    def __init__(self):
        super(Ui, self).__init__("main")
        self.show()
        
        self.JobOption: QComboBox = self.findChild(QComboBox, "comboBox")
        self.ModelName: QComboBox = self.findChild(QComboBox, "comboBox_2")
        
        self.RunButton: QPushButton = self.findChild(QPushButton, "pushButton")
        self.StopButton: QPushButton = self.findChild(QPushButton, "pushButton_2")
        
        self.StopButton.setEnabled(False)
        
        self.RunButton.clicked.connect(self.RunModel)
        
    def RunModel(self):
        self.RunButton.setEnabled(False)
        self.RunButton.setText("Wait")
        if self.JobOption.currentText() == "Fast Food Worker":
            if self.ModelName.currentText() == "Stable":
                Model = ImageRecognitionAI()
                self.RunButton.setText("Running")
                # self.StopButton.setEnabled(True)
                time.sleep(1)
                for _ in range(self.spinBox.value()):
                    if self.checkBox.isChecked():
                        Model.CaptureAndProcessOrderV2()
                    else:
                        Model.CaptureAndProcessOrderV1()
                    time.sleep(4)
        self.RunButton.setEnabled(True)
        self.RunButton.setText("Run")
        
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = Ui()
        app.exec_()
    except Exception as e:
        msg = QMessageBox() 
        msg.setIcon(QMessageBox.Critical) 
        msg.setWindowTitle("Warning")
        msg.setText("Unhandled Error: " + str(e)) 
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  
        retval = msg.exec_() 