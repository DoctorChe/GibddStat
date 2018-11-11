#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Окно о программе"""
from PyQt5 import QtWidgets, QtCore, QtGui

from ui.ui_aboutwindow import Ui_AboutWindow


class AboutWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent,
                                   flags=QtCore.Qt.Window)
        self.ui = Ui_AboutWindow()
        self.ui.setupUi(self)
        self.ui.label_logo.setPixmap(QtGui.QPixmap("logo.png"))
