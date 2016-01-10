from PyQt5 import QtWidgets
from UI.HelpDialogUI import Ui_Dialog


class FinalMeta(type(QtWidgets.QDialog), type(Ui_Dialog)):
    pass


class HelpDialogController(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.connectSignals()

    def connectSignals(self):
        self.okButton.clicked.connect(self.okClicked)

    def okClicked(self):
        self.hide()
