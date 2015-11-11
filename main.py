from PyQt5 import QtWidgets
import UI.MainWindow
import sys

__author__ = 'Piotr Gomola'


app = QtWidgets.QApplication(sys.argv)
mainWindow = QtWidgets.QMainWindow()
ui = UI.MainWindow.Ui_MainWindow()
ui.setupUi(mainWindow)
mainWindow.show()
sys.exit(app.exec_())
