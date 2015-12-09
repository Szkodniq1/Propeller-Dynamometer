from PyQt5 import QtWidgets
from UI.CalibrateDialogUI import Ui_Dialog


class FinalMeta(type(QtWidgets.QDialog), type(Ui_Dialog)):
    pass


class CalibrateDialogController(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
