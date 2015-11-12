from PyQt5 import QtWidgets
import UI.MainWindow
import sys
import serial
import Functions.SerialFunctions

__author__ = 'Piotr Gomola'


def fill_ports_list():
        for portname in Functions.SerialFunctions.enumerateSerialPorts():
            ui.uartPortList.addItem(portname)


app = QtWidgets.QApplication(sys.argv)
mainWindow = QtWidgets.QMainWindow()
ui = UI.MainWindow.Ui_MainWindow()
ui.setupUi(mainWindow)
mainWindow.show()
fill_ports_list()


sys.exit(app.exec_())



