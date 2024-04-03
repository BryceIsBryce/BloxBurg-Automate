from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys

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
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()