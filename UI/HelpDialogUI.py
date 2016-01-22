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
        Dialog.resize(453, 536)
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setGeometry(QtCore.QRect(180, 500, 93, 28))
        self.okButton.setObjectName("okButton")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 441, 491))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 411, 391))
        self.label.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 411, 381))
        self.label_2.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.label_3 = QtWidgets.QLabel(self.tab_3)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 411, 441))
        self.label_3.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.tabWidget.addTab(self.tab_3, "")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Pomoc"))
        self.okButton.setText(_translate("Dialog", "OK"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p>Upewnij się, że urządzenie jest włączone i podłączone do komputera, następnie przy pomocy zakłądki wyboru sposobu komunikacji ustaw parametry połączenia i naciśnij połącz. W momencie gdy prawidłowo podłączono się do urządzenia, w oknie terminala powinien pojawić się odwpowiedni komunikat wraz z ramką odpowiedzi.</p><p><br/></p><p>W przeciwnym wypadku należy upewnić się że urządzenie jest podłączone prawidłowo a parametry połączenia nie są błędne.</p><p><br/></p><p>Połączenie można też nawiązać poprzez linię komend, w celu uzyskania informacji wpisz w niej <span style=\" font-style:italic;\">help.</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Połączenie"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p>Praca manualna to rodzaj pracy podczas której wypełnienie zadajemy ręcznie z programu. Aby ją aktywować należy zaznaczyć okienko <span style=\" font-style:italic;\">Praca manualna.</span> Aktywuje się wtedy panel do obsługi hamowni. Zmieniając wartość początkową, można modulować od jakiej wartości wystartuje test. Klikając start, silniki zaczną pracować. Można wtedy modulować wypełnienie przyciskami sterowania - każdym z osobna lub oboma naraz. Pomiary, o ile zaznaczone było okno zapisu do pliku, będą zapisywane przez cały okres trwania testu.</p><p><br/></p><p>W momencie startu aktywowany jest 10 sekundowy timer. Jeżeli podczas tych 10 sekund nie zajdą żadne zmiany w programie (nie zostaną zanotowane zmiany wypełnienia) to test zostanie automatycznie zakończony. Zostało to wprowadzone w ramach bezpieczeństwa.</p><p><br/></p><p>Pracę manualną można również wystartować i zatrzymać z linii komend. Więcej informacji pokaże się po wpisaniu <span style=\" font-style:italic;\">help.</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "Praca manualna"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p>W celu przeprowadzenia testu ze skryptu, należy wcześniej napisać sam skrypt. Jest to plik tesktowy w którym znajdują się następujący ciąg komend: </p><p>[PWM1,PWM2,TIME] [PWM1,PWM2,TIME] ....</p><p>PWM1 to wartość wypełnienia na pierwszym silniku, PWM2 to wartość wypełnienia na drugim silniku a TIME to czas przez który dana konfiguracja będzie obowiązywać. Oznacza to, że Następna komenda będzie realizowana po czasie podanym w komendzie wcześniej.</p><p>Bardzo ważne jest zachowanie schematu - parametry są oddzielane przecinkie i znajdują się wewnątrz nawiasów kwadratowych. Pomiędzy ramkami jest jedna spacja.</p><p>Następnie gdy plik skryptowy zostanie zapisany w folderze z programem jako plik tekstowy, należy go wczytać z lini komend:</p><p><span style=\" font-style:italic;\">load plik.txt</span></p><p>Komenda ta wczytuje nasz skrypt. Jeżeli skrypt został napisany prawidłowo zostaniemy poinformowani o tym, że skrypt został wczytany poprawnie. W przeciwnym wypadku dostaniemy informaje o błędzie. Gdy skrypt jest już poprawnie załadowany, należy wpisać w lini komend:</p><p><span style=\" font-style:italic;\">start test</span></p><p>Stanowsko pomiarowe powinno zacząć pracę.</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Dialog", "Praca ze skryptu"))

