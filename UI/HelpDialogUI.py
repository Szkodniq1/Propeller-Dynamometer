# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HelpDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(453, 487)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 411, 111))
        self.label.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 130, 411, 141))
        self.label_2.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 250, 411, 111))
        self.label_3.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(20, 370, 411, 61))
        self.label_4.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(170, 450, 93, 28))
        self.okButton.setObjectName("okButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "1. W celu uruchomienia testu na hamowni, należy w pierwszej kolejności podłączyć prawidłowo moduł. Upewnić się iż moduł jest zasilony, a układ moduł-komputer mają wspólną masę. Następnie podłączyć przewód komunikacji. Mając podłączony przewód komunikacji należy w programie podłączyć się w prawidłowej konfiguracji, przy pomocy wybranego sposobu komunikacji oraz przycisku Połącz."))
        self.label_2.setText(_translate("Dialog", "2. W razie błędnych ustawien lub problemów, terminal powiadomi użytkownika o problemie. W przypadku gdy wszystko przebiegło prawidłowo, komunikacja została nawiązana a w oknie terminala powinien pojawić się komunikat o nawiązaniu połączenia z modułem. W przypadku gdy połączenie zostało nawiązane a w terminalu nic się nie pojawiło, może to oznaczać błędny wybór portu lub prędkości transmiji."))
        self.label_3.setText(_translate("Dialog", "3. Po prawidłowym nawiązaniu połączenia należy wpisać parametry testu, skalibrować tensometr wybrać czy i które parametry mają być zapisywane do pliku oraz wybrać jego nazwę. W momencie gdy wszystko to zostało wykonane, można przejść do testów przy pomocy przycisku Start. Testy powinny zostać rozpoczęte, w przeciwnym wypadku, należy powonie wykonać wszystkie wymienione w tym punkcie czynności."))
        self.label_4.setText(_translate("Dialog", "4. Program poinformuje użytkownika o zakończeniu testów. W razie wystąpienia problemów, może skorzystać z wyłączenia testu poprzez przycisk STOP, lub korzystając z fizycznego przycisku awaryjnego modułu."))
        self.okButton.setText(_translate("Dialog", "OK"))

