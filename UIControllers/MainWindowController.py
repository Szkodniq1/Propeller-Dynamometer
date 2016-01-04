from PyQt5 import QtCore, QtWidgets
from datetime import datetime
import serial
import serial.tools.list_ports
import Functions.SerialFunctions
from serial.serialutil import SerialException
import threading
from UIControllers.CalibrateDialogController import CalibrateDialogController
import usb.core
import usb.util
import Functions.MiscFunctions
import Utils.ComunicationUtils
from UI.MainWindowUI import Ui_MainWindow

__author__ = 'Piotr Gomola'


class FinalMeta(type(QtWidgets.QMainWindow), type(Ui_MainWindow)):
    pass


class MainWindowController(QtWidgets.QMainWindow, Ui_MainWindow, metaclass=FinalMeta):

    ser = serial.Serial
    thread = None
    alive = threading.Event()
    file = None
    dev = None
    epWrite = None
    epRead = None
    message = []

    def __init__(self, parent=None):
        super(MainWindowController, self).__init__(parent)
        self.setupUi(self)
        self.fill_ports_list()
        self.connectSignals()

    def fill_ports_list(self):
        for portname in Functions.SerialFunctions.enumerateSerialPorts():
            self.uartPortList.addItem(portname)

    def connectSignals(self):
        self.saveToFile.stateChanged.connect(self.saveToFileStateChanged)
        self.connectButton.clicked.connect(self.connectButtonPushed)
        self.stopButton.clicked.connect(self.stopButtonAction)
        self.calibrateTens.clicked.connect(self.calibrate)
        self.startTest.clicked.connect(self.startClicked)

    def saveToFileStateChanged(self, state):

        if state == 0:
            self.groupBox.setEnabled(False)
            self.logSomething(': Zapisywanie plikow wylaczone')
        else:
            self.groupBox.setEnabled(True)
            self.logSomething(': Zapisywanie plikow wlaczone')

    def connectButtonPushed(self):
        if self.usb_hid.isHidden():
            self.uartConnection()
        else:
            self.usbHIDConnection()

    def uartConnection(self):
        cur_item = self.uartPortList.currentText()
        if self.connectButton.text() == u"Połącz":
            self.connectButton.setText(u"Rozłącz")
            if cur_item is not None:
                fullname = Functions.SerialFunctions.fullPortName(cur_item)
                try:
                    self.tabWidget.setEnabled(False)
                    self.ser = serial.Serial(port=fullname, baudrate=9600, timeout=None, writeTimeout=3)
                    self.logSomething('Opened %s successfully' % cur_item)
                    self.StartThread()
                    if self.groupBox.isEnabled():
                        self.file = open("pomiary.txt", 'w')
                        self.writeToFile('Speed', 'Current', 'Voltage', 'Pressure')
                except SerialException as e:
                    self.logSomething('%s error:\n %s' % (cur_item, e))
                    self.tabWidget.setEnabled(True)
                    self.connectButton.setText(u"Połącz")

        else:
            self.connectButton.setText(u"Połącz")
            if self.ser.isOpen():
                self.StopThread()
                self.tabWidget.setEnabled(True)
                self.ser.close()
                self.logSomething('Closed %s successfully' % cur_item)
                if self.groupBox.isEnabled():
                    self.file.close()

    def usbHIDConnection(self):
        if self.vendorID.text() is not "" and self.productID.text() is not "" and len(
                self.vendorID.text()) is 4 and len(self.productID.text()) is 4:
            vendorId = Functions.MiscFunctions.stringToHex(self.vendorID.text())  # 0x477
            productId = Functions.MiscFunctions.stringToHex(self.productID.text())  # 0x5620
            if self.connectButton.text() == u"Połącz":
                self.connectButton.setText(u"Rozłącz")
                self.tabWidget.setEnabled(False)
                self.dev = usb.core.find(idVendor=vendorId, idProduct=productId)
                if self.dev is None:
                    raise ValueError('Device not found')
                # get an endpoint instance
                cfg = self.dev.get_active_configuration()
                intf = cfg[(0, 0)]
                self.epWrite = intf[1]
                self.epRead = intf[0]
                assert self.epWrite is not None
                assert self.epRead is not None
                self.StartThread()
                if self.groupBox.isEnabled():
                    self.file = open("pomiary.txt", 'w')
                    self.writeToFile('Speed', 'Current', 'Voltage', 'Pressure')
            else:
                self.connectButton.setText(u"Połącz")
                self.tabWidget.setEnabled(True)
                self.dev = None
                self.epRead = None
                self.epWrite = None
                self.StopThread()
                if self.groupBox.isEnabled():
                    self.file.close()
        elif self.vendorID.text() is "" or self.productID.text() is "":
            self.logSomething('Please, fill all fileds needed to connect via USB HID.')
        else:
            self.logSomething('VendorId or ProductId have incorrect structure. It should consist of 4 characters.')

    def calibrate(self):
        self.logSomething('Kalibracja!')
        self.dialog = CalibrateDialogController()
        self.dialog.calibrateGetValue.clicked.connect(self.dialogGetValueClicked)
        self.dialog.calibrateInsertValue.clicked.connect(self.dialogInsertValueClicked)
        self.dialog.calibrate.clicked.connect(self.dialogCalibrateClicked)
        self.dialog.show()

    def stopButtonAction(self):
        if self.connectButton.text() == u"Rozłącz":
            Utils.ComunicationUtils.sendEmergencyStop(self.ser)
            self.logSomething("Stop awaryjny")
        else:
            self.logSomething("Połączenie nie zostało nawiązane")

    def StartThread(self):
        """Start the receiver thread"""
        self.thread = threading.Thread(target=self.CommunicationThread)
        self.thread.setDaemon(1)
        self.alive.set()
        self.thread.start()
        self.ser.rts = True
        self.ser.dtr = True

    def StopThread(self):
        """Stop the receiver thread, wait until it's finished."""
        if self.thread is not None:
            self.alive.clear()  # clear alive event for thread
            self.thread.join()  # wait until thread has finished
            self.thread = None

    def CommunicationThread(self):
        """\
        Thread that handles the incoming traffic.
        """
        while self.alive.isSet():
            if self.usb_hid.isHidden():
                data_left = self.ser.inWaiting()  # Get the number of characters ready to be read
                b = self.ser.read(data_left)
                if b:
                    byte = ord(b)
                    # self.logSomething(b)
                    # byte = int(format(ord(b), "x"))
                    if Utils.ComunicationUtils.isStartFrame(byte):
                        self.message = [byte]
                    elif Utils.ComunicationUtils.isStopFrame(byte):
                        self.message.append(byte)
                        self.dataRecieved()
                    else:
                        self.message.append(byte)
            else:
                try:
                    data = self.dev.read(self.epRead, 1000)
                    # print data
                    sret = ''.join([chr(x) for x in data])
                    # print sret
                    self.logSomething(sret)
                except usb.core.USBError as e:
                    data = None
                    if e.args == ('Operation timed out',):
                        continue

    def writeToFile(self, speed=None, current=None, voltage=None, pressure=None):
        if self.saveSpeed.isChecked() and speed is not None:
            self.file.write(speed)
            if (self.saveCurrent.isChecked() or self.saveVoltage.isChecked() or self.savePressure.isChecked()):
                self.file.write(';')
        if self.saveCurrent.isChecked() and current is not None:
            self.file.write(current)
            if (self.saveVoltage.isChecked() or self.savePressure.isChecked()):
                self.file.write(';')
        if self.saveVoltage.isChecked() and voltage is not None:
            self.file.write(voltage)
            if (self.savePressure.isChecked()):
                self.file.write(';')
        if self.savePressure.isChecked() and pressure is not None:
            self.file.write(pressure)
        self.file.write('\n')

    def dialogGetValueClicked(self):
        if self.connectButton.text() == u"Rozłącz":
            Utils.ComunicationUtils.sendGetValue(self.ser)
            self.logSomething("Wysłano rządanie podania wartości z tensometru")
        else:
            self.logSomething("Połączenie nie zostało nawiązane")

    def dialogInsertValueClicked(self):
        self.logSomething("Insert")

    def dialogCalibrateClicked(self):
        if self.connectButton.text() == u"Rozłącz":
            Utils.ComunicationUtils.sendFunctionParameters(self.ser, 1297.04179, -686.12367)
            self.logSomething("Wysłano parametry funkcji: y="+str(self.dialog.a)+"x+"+str(self.dialog.b))
        else:
            self.logSomething("Połączenie nie zostało nawiązane")

    def logSomething(self, string):
        self.terminal.appendPlainText(datetime.now().strftime("%H:%M:%S.%f") + ': ' + string)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def dataRecieved(self):
        string = "[%s]" % ", ".join(map(str,self.message))
        self.logSomething(string)

    def startClicked(self):
        if self.connectButton.text() == u"Rozłącz":
            Utils.ComunicationUtils.sendStartTest(self.ser)
            self.logSomething("Start testu")
        else:
            self.logSomething("Połączenie nie zostało nawiązane")

