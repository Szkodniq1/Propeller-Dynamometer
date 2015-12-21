from PyQt5 import QtWidgets
import sys
from UIControllers.MainWindowController import MainWindowController


__author__ = 'Piotr Gomola'

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    mainWindow = MainWindowController()
    mainWindow.show()
    sys.exit(app.exec_())
