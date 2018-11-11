# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_aboutwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutWindow(object):
    def setupUi(self, AboutWindow):
        AboutWindow.setObjectName("AboutWindow")
        AboutWindow.resize(451, 167)
        self.label = QtWidgets.QLabel(AboutWindow)
        self.label.setGeometry(QtCore.QRect(160, 20, 221, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_version = QtWidgets.QLabel(AboutWindow)
        self.label_version.setGeometry(QtCore.QRect(160, 50, 211, 17))
        self.label_version.setObjectName("label_version")
        self.label_description = QtWidgets.QLabel(AboutWindow)
        self.label_description.setGeometry(QtCore.QRect(160, 70, 361, 61))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_description.setFont(font)
        self.label_description.setTextFormat(QtCore.Qt.AutoText)
        self.label_description.setObjectName("label_description")
        self.label_copiright = QtWidgets.QLabel(AboutWindow)
        self.label_copiright.setGeometry(QtCore.QRect(160, 130, 211, 17))
        self.label_copiright.setObjectName("label_copiright")
        self.widget_logo = QtWidgets.QWidget(AboutWindow)
        self.widget_logo.setGeometry(QtCore.QRect(10, 10, 141, 141))
        self.widget_logo.setObjectName("widget_logo")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_logo)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_logo = QtWidgets.QVBoxLayout()
        self.verticalLayout_logo.setObjectName("verticalLayout_logo")
        self.label_logo = QtWidgets.QLabel(self.widget_logo)
        self.label_logo.setText("")
        self.label_logo.setPixmap(QtGui.QPixmap("logo.png"))
        self.label_logo.setScaledContents(True)
        self.label_logo.setObjectName("label_logo")
        self.verticalLayout_logo.addWidget(self.label_logo)
        self.horizontalLayout.addLayout(self.verticalLayout_logo)

        self.retranslateUi(AboutWindow)
        QtCore.QMetaObject.connectSlotsByName(AboutWindow)

    def retranslateUi(self, AboutWindow):
        _translate = QtCore.QCoreApplication.translate
        AboutWindow.setWindowTitle(_translate("AboutWindow", "О программе"))
        self.label.setText(_translate("AboutWindow", "Парсер сайта статистики ГИБДД"))
        self.label_version.setText(_translate("AboutWindow", "Версия 1.0"))
        self.label_description.setText(_translate("AboutWindow", "<html><head/><body><p>Парсер сайта статистики ГИБДД - <br>программа для сбора и анализа данных <br>с официального веб-сайта Госавтоинспекции</p></body></html>"))
        self.label_copiright.setText(_translate("AboutWindow", "Copiright (C) 2018"))

