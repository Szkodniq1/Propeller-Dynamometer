# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CalibrateDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(600, 400))
        Dialog.setMaximumSize(QtCore.QSize(600, 400))
        self.insertedWeight = QtWidgets.QLineEdit(Dialog)
        self.insertedWeight.setGeometry(QtCore.QRect(330, 30, 111, 31))
        self.insertedWeight.setObjectName("insertedWeight")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(330, 10, 201, 16))
        self.label_2.setObjectName("label_2")
        self.calibrate = QtWidgets.QPushButton(Dialog)
        self.calibrate.setGeometry(QtCore.QRect(440, 360, 141, 28))
        self.calibrate.setObjectName("calibrate")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 251, 16))
        self.label.setObjectName("label")
        self.calibrateInsertValue = QtWidgets.QPushButton(Dialog)
        self.calibrateInsertValue.setGeometry(QtCore.QRect(460, 30, 121, 31))
        self.calibrateInsertValue.setObjectName("calibrateInsertValue")
        self.calibrateGetValue = QtWidgets.QPushButton(Dialog)
        self.calibrateGetValue.setGeometry(QtCore.QRect(140, 30, 111, 31))
        self.calibrateGetValue.setObjectName("calibrateGetValue")
        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(10, 80, 580, 270))
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.tableView.setTextElideMode(QtCore.Qt.ElideRight)
        self.tableView.setSortingEnabled(False)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setDefaultSectionSize(290)
        self.tableView.horizontalHeader().setMinimumSectionSize(290)
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.measurements = QtWidgets.QLineEdit(Dialog)
        self.measurements.setEnabled(False)
        self.measurements.setGeometry(QtCore.QRect(10, 30, 111, 31))
        self.measurements.setObjectName("measurements")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Kalibracja"))
        self.label_2.setText(_translate("Dialog", "Nominalna wrtość odważnika [g]:"))
        self.calibrate.setText(_translate("Dialog", "Kalibruj"))
        self.label.setText(_translate("Dialog", "Zmierona wartość na przetworniku [reg] :"))
        self.calibrateInsertValue.setText(_translate("Dialog", "Wprowadź pomiar"))
        self.calibrateGetValue.setText(_translate("Dialog", "Dokonaj pomiaru"))

