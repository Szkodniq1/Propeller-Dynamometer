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
import Utils.CommandUtils
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
    manualWorkData = ["0","0"]
    testDataFrame = ["0","0"]
    loadTest = [[],[],[]]
    underWorkFlag = False
    isManualWork =False
    timer = None
    timerIterator = 0

    def __init__(self, parent=None):
        super(MainWindowController, self).__init__(parent)
        self.setupUi(self)
        self.fill_ports_list()
        self.connectSignals()
        self.manualWorkStateChanged(False)
        self.terminal.clear()
        self.tabWidget.widget(1).setEnabled(False)
        self.logSomething("Aby zobaczyc dostepne komendy wpisz: help")

    def fill_ports_list(self):
        for portname in Functions.SerialFunctions.enumerateSerialPorts():
            self.uartPortList.addItem(portname)

    def connectSignals(self):
        self.saveToFile.stateChanged.connect(self.saveToFileStateChanged)
        self.connectButton.clicked.connect(self.connectButtonPushed)
        self.stopButton.clicked.connect(self.stopButtonAction)
        self.manualWork.stateChanged.connect(self.manualWorkStateChanged)
        self.calibrateTens.clicked.connect(self.calibrate)
        self.actionZamknij.triggered.connect(self.closeWindow)
        self.actionPomoc.triggered.connect(self.helpClicked)
        self.actionAutorzy.triggered.connect(self.authorsClicked)
        self.quickSend.clicked.connect(self.interpretLineMessage)
        self.quickMessage.returnPressed.connect(self.interpretLineMessage)
        self.rescanButton.clicked.connect(self.rescanButtonClicked)
        self.actionManual.clicked.connect(self.actionManualClicked)
        self.engOneMin.clicked.connect(self.engOneMinClicked)
        self.engOnePlus.clicked.connect(self.engOnePlusClicked)
        self.engTwoMin.clicked.connect(self.engTwoMinClicked)
        self.engTwoPlus.clicked.connect(self.engTwoPlusClicked)
        self.engBothMin.clicked.connect(self.engBothMinClicked)
        self.engBothPlus.clicked.connect(self.engBothPlusClicked)

    def actionManualClicked(self):
        if self.actionManual.text() == "START":
            self.manualWorkData[0] = str(self.engOneInit.value())
            self.manualWorkData[1] = str(self.engTwoInit.value())
            if self.checkAndSendParameters(self.poleNumber.text(), self.poleNumberTwo.text(), self.safetyTime.value()):
                self.actionManual.setText("STOP")
                self.logSomething('Start pracy manualnej')
        else:
            Utils.ComunicationUtils.sendStop(self.ser)
            self.actionManual.setText("START")
            self.logSomething('Stop pracy manualnej')

    def rescanButtonClicked(self):
        self.uartPortList.clear()
        for portname in Functions.SerialFunctions.enumerateSerialPorts():
            self.uartPortList.addItem(portname)

    def saveToFileStateChanged(self, state):
        if state == 0:
            self.groupBox.setEnabled(False)
            self.logSomething('Zapisywanie plikow wylaczone')
        else:
            self.groupBox.setEnabled(True)
            self.logSomething('Zapisywanie plikow wlaczone')

    def manualWorkStateChanged(self, state):
        if state == 0:
            if not self.underWorkFlag:
                self.manualGroupBox.setEnabled(False)
                self.logSomething('Praca manualna wylaczona')
            else:
                self.logSomething('Nie mozna zmieniac stanu pracy manualnej podczas trwania testu.')
        else:
            if not self.underWorkFlag:
                self.manualGroupBox.setEnabled(True)
                self.logSomething('Praca manualna wlaczona')
                self.isManualWork = True
            else:
                self.logSomething('Nie mozna zmieniac stanu pracy manualnej podczas trwania testu.')

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
                    self.logSomething('Otwarto port %s' % cur_item)
                    self.StartThread()
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
                self.logSomething('Zamknieto port %s' % cur_item)
                self.ser = None

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
            self.logSomething("Polaczenie nie zostalo nawiazane")

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
        if self.usb_hid.isHidden():
            Utils.ComunicationUtils.sendConnected(self.ser)
        while self.alive.isSet():
            if self.usb_hid.isHidden():
                data_left = self.ser.inWaiting()
                b = self.ser.read(data_left)
                if len(b) > 0:
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

    def writeToFile(self, pwm1=None, pwm2 = None, speed1=None, speed2=None, current1=None, current2=None, voltage=None,pressure=None):
        if self.file is not None:
            self.file.write(pwm1)
            self.file.write(';')
            self.file.write(pwm2)
            if (self.saveSpeed.isChecked() or self.saveCurrent.isChecked() or self.saveVoltage.isChecked() or self.savePressure.isChecked()):
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
            self.logSomething("Wyslano rzadanie podania wartosci z tensometru")
        else:
            self.logSomething("Polaczenie nie zostalo nawiazane")

    def dialogInsertValueClicked(self):
        self.logSomething("Dodano pomiar!")

    def dialogCalibrateClicked(self):
        if self.connectButton.text() == u"Rozłącz":
            if self.dialog.a is not None:
                Utils.ComunicationUtils.sendFunctionParameters(self.ser, self.dialog.a, self.dialog.b)
                self.logSomething("Wyslano parametry funkcji: y=" + str(self.dialog.a) + "x+" + str(self.dialog.b))
                file = open("config.txt", 'w')
                file.write("ParamA="+str(self.dialog.a)+"\n")
                file.write("ParamB="+str(self.dialog.b)+"\n")
                file.close()
            else:
                self.logSomething("Za malo pomiarow")
        else:
            self.logSomething("Polaczenie nie zostalo nawiazane")

    def logSomething(self, string):
        self.terminal.appendPlainText(datetime.now().strftime("%H:%M:%S.%f") + ': ' + string)
        self.terminal.selectAll()
        cursor = self.terminal.textCursor()
        cursor.clearSelection()
        self.terminal.setTextCursor(cursor)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def dataRecieved(self, data):
        # string = "[%s]" % ", ".join(map(str, data))
        # self.logSomething(string)
        if (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.MEASURE:
            self.getMeassuresAndSaveThem(data)
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.CALIBRATE_GET_VALUE:
            self.logSomething('Otrzymano wartosc')
            self.putValueToCalibrateDialog(data)
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.SET_TEST_PARAMS:
            self.openFileAndStartTest()
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.CONNECTION:
            self.connectedToDevice()
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.START_TEST:
            self.startTestRecieved()
        elif (data[1] & Utils.ComunicationUtils.FUNCTION_MASK) == Utils.ComunicationUtils.STOP_TEST:
            self.testStopped()
        else:
            self.logSomething('Nieznany komunikat')

    def startTestRecieved (self):
        self.logSomething('Start testu')
        self.underWorkFlag = True
        if self.isManualWork:
            Utils.ComunicationUtils.sendPWMFrame(self.ser,self.manualWorkData)
        else:
            self.timerIterator = 0
            self.testDataFrame = [self.loadTest[0][self.timerIterator],self.loadTest[1][self.timerIterator]]
            Utils.ComunicationUtils.sendPWMFrame(self.ser,self.testDataFrame)
            self.timer = threading.Timer(float(self.loadTest[2][self.timerIterator])/1000,self.timerInterrupt)
            self.timer.start()

    def timerInterrupt (self):
        self.timer.cancel()
        self.timerIterator += 1
        if self.timerIterator < len(self.loadTest[0]):
            self.testDataFrame = [self.loadTest[0][self.timerIterator],self.loadTest[1][self.timerIterator]]
            Utils.ComunicationUtils.sendPWMFrame(self.ser,self.testDataFrame)
            self.timer = threading.Timer(float(self.loadTest[2][self.timerIterator])/1000,self.timerInterrupt)
            self.timer.start()
        elif self.timerIterator == len(self.loadTest[0]):
            Utils.ComunicationUtils.sendStop(self.ser)

    def testStopped (self):
        self.groupBox.setEnabled(True)
        self.saveToFile.setEnabled(True)
        self.logSomething("Koniec testu")
        if self.file is not None:
            self.logSomething('Zamknieto plik')
            self.file.close()
            self.file = None
        if self.actionManual.text() == "STOP":
            self.actionManual.setText("START")
        self.underWorkFlag = False

    def connectedToDevice (self):
        self.logSomething("Podlaczono do urzadzenia")
        try:
            f = open("config.txt",'r')
            self.logSomething("Wczytano plik konfiguracyjny.")
            firstLine = f.readline()
            splitOne = firstLine.split("=")
            paramA = float(splitOne[1])
            secondLine = f.readline()
            splitTwo = secondLine.split("=")
            paramB = float(splitTwo[1])
            Utils.ComunicationUtils.sendFunctionParameters(self.ser, paramA, paramB)
            f.close()
        except FileNotFoundError as e:
            self.logSomething("Nie znaleziono pliku konfiguracyjnego.")
            self.logSomething('Przed rozpoczeciem testow skalibruj tensometr.')

    def openFileAndStartTest (self):
        if self.groupBox.isEnabled():
            self.groupBox.setEnabled(False)
            self.saveToFile.setEnabled(False)
            if self.fileName.text() is not None and self.fileName.text() != "":
                filename = self.fileName.text() + ".txt"
                self.file = open(filename, 'w')
                self.writeToFile('pwm1', 'pwm2', 'n1', 'n2', 'I1', 'I2', 'U', 'm')
            else:
                self.logSomething("Test zostanie zapisany z nazwa aktualnej daty")
                self.file = open(datetime.now().strftime("%y%m%d%H%M%S") + ".txt", 'w')
                self.writeToFile('pwm1', 'pwm2', 'n1', 'n2', 'I1', 'I2', 'U', 'm')
        Utils.ComunicationUtils.sendStartTest(self.ser)

    def checkAndSendParameters(self, poleNumberText, poleNumberTwoText, safetyTime):
        if self.connectButton.text() == u"Rozłącz":
            if self.poleNumber is not None:
                pNumber = int(poleNumberText)
                pNumber2 = int(poleNumberTwoText)
            if pNumber > 1:
                Utils.ComunicationUtils.sendTestParameters(self.ser, pNumber, pNumber2, safetyTime)
                self.logSomething("Parametry testu wyslane")
                return True
            else:
                self.logSomething("Zla wartosc liczby par biegunow")
                return False
        else:
            self.logSomething("Polaczenie nie zostalo nawiazane")
            return False

    def putValueToCalibrateDialog(self, data):
        i = data[1] & Utils.ComunicationUtils.NUMBER_MASK
        i += 2
        meassure = 0
        # meassure = (data[2] & Utils.ComunicationUtils.DATA_MASK)+((data[3] & Utils.ComunicationUtils.DATA_MASK)<<7)+((data[4] & Utils.ComunicationUtils.DATA_MASK)<<14)
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
        i1 = ((data[oldI + 1] & Utils.ComunicationUtils.DATA_MASK) + float("{0:.2f}".format((
        (data[oldI + 2] & Utils.ComunicationUtils.DATA_MASK) / 100 - int((
        (data[oldI + 2] & Utils.ComunicationUtils.DATA_MASK) / 100))))))
        i2 = ((data[oldI + 3] & Utils.ComunicationUtils.DATA_MASK) + float("{0:.2f}".format(((
        (data[oldI + 4] & Utils.ComunicationUtils.DATA_MASK) / 100)- int((
        (data[oldI + 4] & Utils.ComunicationUtils.DATA_MASK) / 100))))))
        v = ((data[oldI + 5] & Utils.ComunicationUtils.DATA_MASK) + float("{0:.2f}".format((
        (data[oldI + 6] & Utils.ComunicationUtils.DATA_MASK) / 100- int((
        (data[oldI + 6] & Utils.ComunicationUtils.DATA_MASK) / 100))))))
        oldI = i + 1
        i += data[i] & Utils.ComunicationUtils.NUMBER_MASK
        i += 1
        p = 0
        #PWM1 i PWM2 w ramce z naciskiem
        for j in range(oldI+1, oldI+4):
            jumpBit = (7 * (j - (oldI+1)))
            parsedData = (data[j] & Utils.ComunicationUtils.DATA_MASK)
            p += parsedData << jumpBit
        if (data[oldI] & Utils.ComunicationUtils.DATA_MASK) == 0x01:
            p*=(-1)
        pwm1 = (data[oldI+4] & Utils.ComunicationUtils.DATA_MASK)
        pwm2 = (data[oldI+5] & Utils.ComunicationUtils.DATA_MASK)
        self.printMeasuresInLabels(str(pwm1), str(pwm2), str(n1), str(n2), str(i1), str(i2), str(v), str(p))
        self.writeToFile(str(pwm1), str(pwm2), str(n1), str(n2), str(i1), str(i2), str(v), str(p))

    def closeWindow(self):
        self.close()

    def helpClicked(self):
        self.helpDialog = HelpDialogController()
        self.helpDialog.show()

    def authorsClicked(self):
        self.auhtorsDialog = AuthorsDialogController()
        self.auhtorsDialog.show()

    def printMeasuresInLabels(self, pwm1, pwm2, speed1, speed2, current1, current2, voltage, pressure):
        self.PWMFirstMeter.setText(pwm1)
        self.PWMSecondMeter.setText(pwm2)
        self.speedMeterN1.setText(speed1)
        self.speedMeterN2.setText(speed2)
        self.currentMeterI1.setText(current1)
        self.currentMeterI2.setText(current2)
        self.voltageMeter.setText(voltage)
        self.pressureMeter.setText(pressure)

    def interpretLineMessage(self):
        message = self.quickMessage.text()
        self.logSomething("CMD: " + message)
        spl = message.split(' ')
        if spl[0] == Utils.CommandUtils.CONNECT_COMMAND:
            self.interpretConnectComman(spl)
        elif spl[0] == Utils.CommandUtils.START_COMMAND:
            self.interpretStartCommand(spl)
        elif spl[0] == Utils.CommandUtils.HELP_COMMAND:
            self.interpretHelpCommand(spl)
        elif spl[0] == Utils.CommandUtils.LOAD_COMMAND:
            self.interpretLoadCommand(spl)
        elif spl[0] == Utils.CommandUtils.STOP_COMMAND:
            self.interpretStopCommand(spl)
        elif spl[0] == Utils.CommandUtils.CLEAR_COMMAND:
            self.interpretClearCommand(spl)
        elif spl[0] == "crash":
            crashThisShit()
        else:
            self.logSomething("Bledna komenda")
        self.quickMessage.clear()

    def interpretClearCommand(self,spl):
        if len(spl) is 1:
            self.terminal.clear()
        else:
            self.logSomething("Bledna liczba przesylanych danych")

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
        if len(spl) is 2:
            if spl[1] == "manual" and not self.underWorkFlag:
                if not self.manualWork.isChecked():
                    self.manualWork.setChecked(True)
                if self.actionManual.text() == "START":
                    self.manualWorkData[0] = str(self.engOneInit.value())
                    self.manualWorkData[1] = str(self.engTwoInit.value())
                    if self.checkAndSendParameters(self.poleNumber.text(), self.poleNumberTwo.text(), self.safetyTime.value()):
                        self.actionManual.setText("STOP")
                        self.logSomething('Start pracy manualnej')
            elif spl[1] == "test" and not self.underWorkFlag:
                if len(self.loadTest[0]) > 0:
                    if self.manualWork.isChecked():
                        self.manualWork.setChecked(False)
                    if self.isManualWork:
                        self.isManualWork = False
                    if self.checkAndSendParameters(self.poleNumber.text(), self.poleNumberTwo.text(), self.safetyTime.value()):
                        self.logSomething('Start testu')
                else:
                    self.logSomething('Test nie zostal zaladowany, lub zaladowal sie blednie')

        else:
            self.logSomething("Bledna liczba przesylanych danych")

    def interpretHelpCommand(self, spl):
        if len(spl) is 1:
            self.logSomething("Pierwszy czlon to komenda, kolejne czlony to parametry")
            self.logSomething("connect [uart,usb] [serialport,vendorId] [baudrate,productId] - polaczenie do portu")
            self.logSomething("load [file.txt, absolut_path\\file.txt] - wczytanie testu z pliku")
            self.logSomething("start [manual, test] - start testu lub pracy manualnej")
            self.logSomething("stop [manual] - stop pracy manualnej")
            self.logSomething("clear - czyszcenie termianala")
        else:
            self.logSomething("Bledna liczba przesylanych danych")

    def interpretLoadCommand(self,spl):
        if len(spl) is 2:
            try:
                f = open(spl[1],'r')
                self.logSomething("Wczytano test z pliku.")
                testText = f.read()
                commands = testText.split(' ')
                if self.checkIfCommandsHaveCorrectShape(commands):
                    for i in range(0,len(commands)):
                        pwmFirst = commands[i].split(',')[0][1:]
                        pwmSecond = commands[i].split(',')[1]
                        time = commands[i].split(',')[2][:-1]
                        if  self.checkIfParamsAreCorrect(pwmFirst,pwmSecond,time,i):
                            if i is 0:
                                self.loadTest = [[],[],[]]
                            self.loadTest[0].append(pwmFirst)
                            self.loadTest[1].append(pwmSecond)
                            self.loadTest[2].append(time)
                            if i is len(commands)-1:
                                self.logSomething("Parametry testu zostaly wczytane poprawnie.")


            except FileNotFoundError as e:
                self.logSomething("Nie znaleziono pliku.")

        else:
            self.logSomething("Bledna liczba przesylanych danych")

    def interpretStopCommand(self,spl):
        if len(spl) is 2:
            if spl[1] == "manual":
                if self.actionManual.text() == "STOP":
                    Utils.ComunicationUtils.sendStop(self.ser)
                    self.actionManual.setText("START")
                    self.logSomething('Stop pracy manualnej')
        else:
            self.logSomething("Bledna liczba przesylanych danych")

    def checkIfParamsAreCorrect(self,pwmFirst,pwmSecond,time,i):
        if int(pwmFirst) < 0 or int(pwmFirst) > 100:
            self.logSomething("Blad: W "+ (i+1) + " komendzie 1 parametr jest niepoprawny.")
            return False
        if int(pwmSecond) < 0 or int(pwmSecond) > 100:
            self.logSomething("Blad: W "+ (i+1) + " komendzie 2 parametr jest niepoprawny.")
            return False
        if int(time) < 100:
            self.logSomething("Blad: W "+ (i+1) + " komendzie 3 parametr jest niepoprawny.")
            return False
        return True

    def checkIfCommandsHaveCorrectShape(self,commands):
        for i in range(0,len(commands)):
            if len(commands[i].split(',')) is not 3:
                self.logSomething("Blad: " +(i+1)+ " komenda jest niepoprawna.")
                return False
            if commands[i][0] != "[" and commands[i][len(commands[i])-1] != "]":
                self.logSomething("Blad: " +(i+1)+ " komenda jest niepoprawna.")
                return False
            return True

    def engOneMinClicked(self):
        self.manualWorkData[0] = self.manualEquation(self.manualWorkData[0], self.engOneJump.value(), True)
        self.sendManualDataWork()

    def engOnePlusClicked(self):
        self.manualWorkData[0] = self.manualEquation(self.manualWorkData[0], self.engOneJump.value(), False)
        self.sendManualDataWork()

    def engTwoMinClicked(self):
        self.manualWorkData[1] = self.manualEquation(self.manualWorkData[1], self.engTwoJump.value(), True)
        self.sendManualDataWork()

    def engTwoPlusClicked(self):
        self.manualWorkData[1] = self.manualEquation(self.manualWorkData[1], self.engTwoJump.value(), False)
        self.sendManualDataWork()

    def engBothMinClicked(self):
        self.doubleManualEquation(True)
        self.sendManualDataWork()

    def engBothPlusClicked(self):
        self.doubleManualEquation(False)
        self.sendManualDataWork()

    def manualEquation(self, data, jump, sub):
        if self.connectButton.text() == u"Rozłącz":
            if sub:
                number = int(data) - jump
                if number < 0:
                    number = 0
                data = str(number)
                return data
            else:
                number = int(data) + jump
                if number > 100:
                    number = 100
                data = str(number)
                return data
        else:
            self.logSomething("Polaczenie nie zostalo nawiazane")
            return data

    def doubleManualEquation(self, sub):
        if self.connectButton.text() == u"Rozłącz":
            if sub:
                number1 = int(self.manualWorkData[0]) - self.engBothJump.value()
                number2 = int(self.manualWorkData[1]) - self.engBothJump.value()
                if number1 < 0:
                    number1 = 0
                if number2 < 0:
                    number2 = 0
                self.manualWorkData[0] = str(number1)
                self.manualWorkData[1] = str(number2)
            else:
                number1 = int(self.manualWorkData[0]) + self.engBothJump.value()
                number2 = int(self.manualWorkData[1]) + self.engBothJump.value()
                if number1 > 100:
                    number1 = 100
                if number2 > 100:
                    number2 = 100
                self.manualWorkData[0] = str(number1)
                self.manualWorkData[1] = str(number2)
        else:
            self.logSomething("Polaczenie nie zostalo nawiazane")

    def sendManualDataWork(self):
        if self.connectButton.text() == u"Rozłącz":
            Utils.ComunicationUtils.sendPWMFrame(self.ser, self.manualWorkData)
        else:
            self.logSomething("Polaczenie nie zostalo nawiazane")

    def closeEvent(self,event):
        self.logSomething('Program zostal zamkniety')
        if self.file is not None:
            self.logSomething('Zamknieto plik')
            self.file.close()
            self.file = None
        if self.connectButton.text() == u"Rozłącz":
            self.connectButtonPushed()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    mainWindow = MainWindowController()
    mainWindow.show()
    sys.exit(app.exec_())
