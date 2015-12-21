from PyQt5 import QtWidgets
from UI.CalibrateDialogUI import Ui_Dialog
from Models.TableModel import TableModel


class FinalMeta(type(QtWidgets.QDialog), type(Ui_Dialog)):
    pass


class CalibrateDialogController(QtWidgets.QDialog, Ui_Dialog):

    measure = '7'
    weight = None
    header = None
    data = None
    tableModel = None

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.connectSignals()
        self.header = [' Wartość zmierzona ', ' Wartość nominalna ']
        self.data = [("","")]
        self.tableModel = TableModel(self,self.data,self.header)
        self.tableView.setModel(self.tableModel)
        self.tableView.horizontalHeader()

    def connectSignals(self):
        self.calibrateGetValue.clicked.connect(self.getValueClicked)
        self.calibrateInsertValue.clicked.connect(self.insertValueClicked)
        self.calibrate.clicked.connect(self.calibrateClicked)

    def getValueClicked(self):
        self.measurements.setText(self.measure)

    def insertValueClicked(self):
        self.weight = self.insertedWeight.text()
        if self.data is [("","")]:
            self.data = [(self.measure,self.weight)]
        else:
            self.data.append((self.measure,self.weight))
        self.tableModel = TableModel(self,self.data,self.header)
        self.tableView.setModel(self.tableModel)

    def calibrateClicked(self):
        self.hide()
