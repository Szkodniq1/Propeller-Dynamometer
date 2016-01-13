from PyQt5 import QtCore, QtWidgets
from datetime import datetime
import sys
import serial
import serial.tools.list_ports
import Functions.SerialFunctions
from serial.serialutil import SerialException
import threading
from UIControllers.CalibrateDialogController import CalibrateDialogController
from UIControllers.HelpDialogController import HelpDialogController
from UIControllers.AuthorsDialogController import AuthorsDialogController
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
    dialog = None
    helpDialog = None
    authorsDialog = None
    message = []
    connectedToDeviceFlag = False

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
        self.actionZamknij.triggered.connect(self.closeWindow)
        self.actionPomoc.triggered.connect(self.helpClicked)
        self.actionAutorzy.triggered.connect(self.authorsClicked)
        self.quickSend.clicked.connect(self.interpretLineMessage)
        self.quickMessage.returnPressed.connect(self.interpretLineMessage)
        self.rescanButton.clicked.connect(self.rescanButtonClicked)

    def rescanButtonClicked(self):
        self.uartPortList.clear()
        for portname in Functions.SerialFunctions.enumerateSerialPorts():
            self.uartPortList.addItem(portname)

    def saveToFileStateChanged(self, state):

        if state == 0:
            self.groupBox.setEnabled(False)
            self.logSomething(': Zapisywanie plikow wylaczone')
        else:
            self.groupBox.setEnabled(True)
            self.logSomething(': Zapisywanie plikow wlaczone')

    def connectButtonPushed(self):
        if self.usb_hid.isHidden():
            self.uartConnection(self.uartPortList.currentText(), int(self.uartBaudRateList.currentText()))
        else:
            self.usbHIDConnection(self.vendorID.text(), self.productID.text())

    def uartConnection(self, cur_item, baudrate):
        if self.connectButton.text() == u"Połącz":
            self.connectButton.setText(u"Rozłącz")
            if cur_item is not None:
                fullname = Functions.SerialFunctions.fullPortName(cur_item)
                try:
                    self.tabWidget.setEnabled(False)

                    self.ser = serial.Serial(port=fullname, baudrate=baudrate, timeout=None, writeTimeout=3)
                    self.logSomething('Opened %s successfully' % cur_item)
                    self.StartThread()

                    Utils.ComunicationUtils.sendConnected(self.ser)
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

    def usbHIDConnection(self, vendorIDText, productIDText):
        if vendorIDText is not "" and productIDText is not "" and len(vendorIDText) is 4 and len(productIDText) is 4:
            vendorId = Functions.MiscFunctions.stringToHex(vendorIDText)  # 0x477
            productId = Functions.MiscFunctions.stringToHex(productIDText)  # 0x5620
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

            else:
                self.connectButton.setText(u"Połącz")
                self.tabWidget.setEnabled(True)
                self.dev = None
                self.epRead = None
                self.epWrite = None
                self.StopThread()

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
                data_left = self.ser.inWaiting()
                b = self.ser.read(data_left)
                if b:
                    for i in range(0, len(b)):
                        if type(b[i]) == int:
                            byte = b[i]
                        elif type(b[i]) == str:
                            byte = ord(b[i])
                        if Utils.ComunicationUtils.isStartFrame(byte):
                            self.message = [byte]
                        elif Utils.ComunicationUtils.isStopFrame(byte):
                            self.message.append(byte)
                            self.dataRecieved(self.message)
                        elif len(self.message) > 500:
                            self.message = []
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

    def writeToFile(self, pwm=None, speed1=None, speed2=None, current1=None, current2=None, voltage=None,
                    pressure=None):
        if self.file is not None:
            self.file.write(pwm)
            self.file.write(';')
            if self.saveSpeed.isChecked() and speed1 is not None and speed2 is not None:
                self.file.write(speed1)
                self.file.write(';')
                self.file.write(speed2)
                if (self.saveCurrent.isChecked() or self.saveVoltage.isChecked() or self.savePressure.isChecked()):
                    self.file.write(';')
            if self.saveCurrent.isChecked() and current1 is not None and current2 is not None:
                self.file.write(current1)
                self.file.write(';')
                self.file.write(current2)
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
        self.logSomething("Dodano pomiar!")

    def dialogCalibrateClicked(self):
        if self.connectButton.text() == u"Rozłącz":
            if self.dialog.a is not None:
                Utils.ComunicationUtils.sendFunctionParameters(self.ser, self.dialog.a, self.dialog.b)
                self.logSomething("Wysłano parametry funkcji: y=" + str(self.dialog.a) + "x+" + str(self.dialog.b))
            else:
                self.logSomething("Za mało pomiarów")
        else:
            self.logSomething("Połączenie nie zostało nawiązane")

    def logSomething(self, string):
        self.terminal.appendPlainText(datetime.now().strftime("%H:%M:%S.%f") + ': ' + string)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def dataRecieved(self, data):
        string = "[%s]" % ", ".join(map(str, data))
        self.logSomething(string)
        if (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.MEASURE:
            self.logSomething('Otrzymano pomiar')
            self.getMeassuresAndSaveThem(data)
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.CALIBRATE_GET_VALUE:
            self.logSomething('Otrzymano wartość')
            self.putValueToCalibrateDialog(data)
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.SET_TEST_PARAMS:
            if self.groupBox.isEnabled():
                self.groupBox.setEnabled(False)
                self.saveToFile.setEnabled(False)
                if self.fileName.text() is not None and self.fileName.text() != "":
                    filename = self.fileName.text() + ".txt"
                    self.file = open(filename, 'w')
                    self.writeToFile('pwm', 'n1', 'n2', 'I1', 'I2', 'V', 'm')
                else:
                    self.logSomething("Test zostanie zapisany z nazwą aktualnej daty")
                    self.file = open(datetime.now().strftime("%y%m%d%H%M%S") + ".txt", 'w')
                    self.writeToFile('pwm', 'n1', 'n2', 'I1', 'I2', 'V', 'm')
            Utils.ComunicationUtils.sendStartTest(self.ser)
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.CONNECTION:
            self.logSomething('Podłączono do urządzenia')
            self.logSomething('Przed rozpoczęciem testów skalibruj tensometr oraz ustaw parametry testu, następnie '
                              'naciśnij przycisk Start.')
            self.connectedToDeviceFlag = True
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.START_TEST:
            self.logSomething('Start testu')
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.STOP_TEST:
            self.groupBox.setEnabled(True)
            self.saveToFile.setEnabled(True)
            self.logSomething("Koniec testu")
            if self.file is not None:
                self.logSomething('Zamknieto plik')
                self.file.close()
        else:
            self.logSomething('Nieznany komunikat')

    def startClicked(self):
        if self.connectButton.text() == u"Rozłącz":
            self.checkAndSendParameters(self.poleNumber.text(), self.poleNumberTwo.text(), self.minPWM.text(), self.maxPWM.text(), self.jumpPWM.text(), self.pwmTime.text())
        else:
            self.logSomething("Połączenie nie zostało nawiązane")

    def checkAndSendParameters(self, poleNumberText, poleNumberTwoText, minPWMText, maxPWMText, jumpPWMText, pwmTimeText):
        if self.poleNumber is not None:
            pNumber = int(poleNumberText)
            pNumber2 = int(poleNumberTwoText)
        if pNumber > 1:
            minPWM = int(minPWMText)
            maxPWM = int(maxPWMText)
            jumpPWM = int(jumpPWMText)
            pwmTime = int(pwmTimeText)
            if 0 <= minPWM < 100 and 0 < maxPWM <= 100 and 0 < jumpPWM < 100 and minPWM < maxPWM and pwmTime > 0:
                Utils.ComunicationUtils.sendTestParameters(self.ser, pNumber, pNumber2, minPWM, maxPWM, jumpPWM, pwmTime)
                self.logSomething("Parametry testu wysłane")
            else:
                self.logSomething("Źle wypełnione wartości PWM")
        else:
            self.logSomething("Zła wartość liczby par biegunów")

    def putValueToCalibrateDialog(self, data):
        i = data[1] & Utils.ComunicationUtils.NUMBER_MASK
        i += 2
        meassure = 0
        for j in range(2, i):
            jumpBit = (7 * (j - 2))
            parsedData = (data[j] & Utils.ComunicationUtils.DATA_MASK)
            meassure += parsedData << jumpBit
        self.dialog.measure = meassure
        self.dialog.measurements.setText(str(meassure))

    def getMeassuresAndSaveThem(self, data):
        i = data[1] & Utils.ComunicationUtils.NUMBER_MASK
        i += 2
        n1 = 0
        n2 = 0
        for j in range(2, i):
            if j < 2 + ((i - 2) / 2):
                jumpBit = (7 * (j - 2))
                parsedData = (data[j] & Utils.ComunicationUtils.DATA_MASK)
                n1 += parsedData << jumpBit
            else:
                jumpBit = int(7 * (j - 2 - ((i - 2) / 2)))
                parsedData = (data[j] & Utils.ComunicationUtils.DATA_MASK)
                n2 += parsedData << jumpBit
        oldI = i
        i += data[i] & Utils.ComunicationUtils.NUMBER_MASK
        i += 1
        i1 = ((data[oldI + 1] & Utils.ComunicationUtils.DATA_MASK) + (
        (data[oldI + 2] & Utils.ComunicationUtils.DATA_MASK) / 100))
        i2 = ((data[oldI + 3] & Utils.ComunicationUtils.DATA_MASK) + (
        (data[oldI + 4] & Utils.ComunicationUtils.DATA_MASK) / 100))
        v = ((data[oldI + 5] & Utils.ComunicationUtils.DATA_MASK) + (
        (data[oldI + 6] & Utils.ComunicationUtils.DATA_MASK) / 100))
        pwm = data[oldI + 7] & Utils.ComunicationUtils.DATA_MASK
        oldI = i + 1
        i += data[i] & Utils.ComunicationUtils.NUMBER_MASK
        i += 1
        p = 0
        for j in range(oldI, i):
            jumpBit = (7 * (j - oldI))
            parsedData = (data[j] & Utils.ComunicationUtils.DATA_MASK)
            p += parsedData << jumpBit
        self.printMeasuresInLabels(str(pwm), str(n1), str(n2), str(i1), str(i2), str(v), str(p))
        self.writeToFile(str(pwm), str(n1), str(n2), str(i1), str(i2), str(v), str(p))

    def closeWindow(self):
        self.close()

    def helpClicked(self):
        self.helpDialog = HelpDialogController()
        self.helpDialog.show()

    def authorsClicked(self):
        self.auhtorsDialog = AuthorsDialogController()
        self.auhtorsDialog.show()

    def printMeasuresInLabels(self, pwm, speed1, speed2, current1, current2, voltage, pressure):
        self.PWMMeter.setText(pwm)
        self.speedMeterN1.setText(speed1)
        self.speedMeterN2.setText(speed2)
        self.currentMeterI1.setText(current1)
        self.currentMeterI2.setText(current2)
        self.voltageMeter.setText(voltage)
        self.pressureMeter.setText(pressure)

    def interpretLineMessage(self):
        message = self.quickMessage.text()
        # self.logSomething(message)
        spl = message.split(',')
        if spl[0] == "connect":
            self.interpretConnectComman(spl)
        elif spl[0] == "start":
            self.interpretStartCommand(spl)
        elif spl[0] == "help":
            self.interpretHelpCommand(spl)
        else:
            self.logSomething("Bledna komenda")
        self.quickMessage.clear()

    def interpretConnectComman(self, spl):
        if len(spl) is 4:
            if spl[1] == "uart":
                self.uartConnection(spl[2], spl[3])
            elif spl[1] == "usb":
                self.usbHIDConnection(spl[2], spl[3])
            else:
                self.logSomething("Bledne parametry")
        else:
            self.logSomething("Bledna liczba przesylanych danych")

    def interpretStartCommand(self, spl):
        if len(spl) is 7:
            self.checkAndSendParameters(spl[1], spl[2], spl[3], spl[4], spl[5], spl[6])
        else:
            self.logSomething("Bledna liczba przesylanych danych")

    def interpretHelpCommand(self, spl):
        if len(spl) is 1:
            self.logSomething("connect,[uart,usb], [serialport,vendorId], [baudrate,productId]")
            self.logSomething("start, [poleNumberOne], [poleNumberTwo], [minimumPWM], [maximumPWM], [jumpPWM], [pwmPeriod]")
        else:
            self.logSomething("Bledna liczba przesylanych danych")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    mainWindow = MainWindowController()
    mainWindow.show()
    sys.exit(app.exec_())
