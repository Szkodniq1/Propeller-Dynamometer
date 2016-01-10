from PyQt5 import QtWidgets
from UI.CalibrateDialogUI import Ui_Dialog
from Models.TableModel import TableModel
import math

class FinalMeta(type(QtWidgets.QDialog), type(Ui_Dialog)):
    pass


class CalibrateDialogController(QtWidgets.QDialog, Ui_Dialog):

    measure = None
    weight = None
    header = None
    data = None
    dataXInt = None
    dataYInt = None
    tableModel = None
    a = None
    b = None
    RR = None

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
        self.calibrateInsertValue.clicked.connect(self.insertValueClicked)
        self.calibrate.clicked.connect(self.calibrateClicked)

    def insertValueClicked(self):
        self.weight = self.insertedWeight.text()
        if self.data == [('', '')]:
            self.data = [(self.measure,self.weight)]
            self.dataXInt = [int(self.measure)]
            self.dataYInt = [int(self.weight)]
        else:
            self.data.append((self.measure,self.weight))
            self.dataXInt.append(int(self.measure))
            self.dataYInt.append(int(self.weight))
        self.tableModel = TableModel(self,self.data,self.header)
        self.tableView.setModel(self.tableModel)
        if len(self.dataXInt) > 1:
            self.a, self.b, self.RR = self.linreg(self.dataXInt, self.dataYInt)

    def calibrateClicked(self):
        self.hide()

    def linreg(self, X, Y):
        """
        Summary
            Linear regression of y = ax + b
        Usage
            real, real, real = linreg(list, list)
        Returns coefficients to the regression line "y=ax+b" from x[] and y[], and R^2 Value
        """
        if len(X) != len(Y):
            raise ValueError('unequal length')
        N = len(X)
        Sx = Sy = Sxx = Syy = Sxy = 0.0
        for i in range(0, len(X)):
            Sx = Sx + X[i]
            Sy = Sy + Y[i]
            Sxx = Sxx + X[i]*X[i]
            Syy = Syy + Y[i]*Y[i]
            Sxy = Sxy + X[i]*Y[i]

        det = Sxx * N - Sx * Sx
        a = (Sxy * N - Sy * Sx)/det
        b = (Sxx * Sy - Sx * Sxy)/det
        meanerror = residual = 0.0
        for i in range(0, len(X)):
            meanerror = meanerror + (Y[i] - Sy/N)**2
            residual = residual + (Y[i] - a * X[i] - b)**2
        RR = 1 - residual/meanerror
        #ss = residual / (N-2)
        #Var_a, Var_b = ss * N / det, ss * Sxx / det
        return a, b, RR
