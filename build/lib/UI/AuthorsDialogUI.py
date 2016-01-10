# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AuthorsDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(384, 214)
        Dialog.setMaximumSize(QtCore.QSize(384, 214))
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 361, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 61, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(30, 70, 81, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(30, 90, 171, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(30, 120, 141, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(30, 140, 221, 16))
        self.label_6.setObjectName("label_6")
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(150, 180, 93, 28))
        self.okButton.setObjectName("okButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Projekt zrealizowany w ramach pracy inżynierskiej 2015/2016"))
        self.label_2.setText(_translate("Dialog", "Autorzy:"))
        self.label_3.setText(_translate("Dialog", "Piotr Gomoła"))
        self.label_4.setText(_translate("Dialog", "piotrsgomola@gmail.com"))
        self.label_5.setText(_translate("Dialog", "Wojciech Maćkowiak"))
        self.label_6.setText(_translate("Dialog", "wojciech.m.mackowiak@gmail.com"))
        self.okButton.setText(_translate("Dialog", "OK"))

