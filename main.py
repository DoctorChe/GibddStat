#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Парсер сайта статистики ГИБДД для сбора и анализа данных"""

import sys
import os
from datetime import datetime
import json
import codecs
from PyQt5 import QtWidgets
from PyQt5 import QtCore
# Импортируем наш интерфейс из файла
from ui.ui_mainwindow import Ui_MainWindow
import GibddStatParser as gibdd


class MainWindow(QtWidgets.QMainWindow):
    """Основной класс программы"""

    def __init__(self, iniFile, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.parser = gibdd.create_parser()
        # namespace = parser.parse_args(sys.argv[1:])
        self.namespace = self.parser.parse_args(sys.argv[1:])
        # self.data_root = self.namespace.dir
        #
        # if not os.path.exists(self.data_root):
        #     os.makedirs(self.data_root)
        #
        # if not os.path.exists(gibdd.log_filename):
        #     gibdd.create_log()
        #
        # if len(self.namespace.updatecodes) > 0:
        #     if self.namespace.updatecodes == "y":
        #         log_text = "Обновление справочника кодов регионов..."
        #         print(log_text)
        #         gibdd.write_log(log_text)
        #         gibdd.save_code_dictionary("regions.json")
        #         log_text = "Обновление справочника завершено"
        #         print(log_text)
        #         gibdd.write_log(log_text)
        #     elif self.namespace.updatecodes == "n":
        #         log_text = "Обновление справочника отменено"
        #         print(log_text)
        #         gibdd.write_log(log_text)
        #
        # # получаем год (если параметр опущен - текущий год)
        # if self.namespace.year is not None:
        #     year = self.namespace.year
        # else:
        #     year = datetime.now().year
        #
        # # получаем месяц (если параметр опущен - все прошедшие месяцы года)
        # if self.namespace.month is not None:
        #     months = [int(self.namespace.month)]
        # else:
        #     if year == str(datetime.now().year):
        #         months = list(range(1, datetime.now().month, 1))
        #     else:
        #         months = list(range(1, 13, 1))
        #
        # # загружаем данные из справочника ОКАТО-кодов регионов и муниципалитетов
        # filename = "regions.json"
        # with codecs.open(filename, "r", "utf-8") as f:
        #     regions = json.loads(json.loads(json.dumps(f.read())))
        #
        #     gibdd.get_dtp_info(self.data_root,
        #                        year,
        #                        months,
        #                        regions,
        #                        region_id=self.namespace.regcode)

    def read_data(self):
        # self.namespace.year = self.ui.
        # self.namespace.month = self.ui.checkBox_updatecodes.isChecked()
        self.namespace.updatecodes = self.ui.checkBox_updatecodes.isChecked()
        self.namespace.dir = ""

    @QtCore.pyqtSlot()
    def show_about_window(self):
        """Отображение окна сведений о программе"""
        return QtWidgets.QMessageBox.about(
            self,
            "О программе",
            "Парсер сайта статистики ГИБДД\nдля сбора и анализа данных\n"
            "Версия 1.0")

    @QtCore.pyqtSlot()
    def show_aboutqt_window(self):
        """Отображение окна сведений о библиотеке Qt"""
        return QtWidgets.QMessageBox.aboutQt(self)


if __name__ == "__main__":
    # QApplication.setDesktopSettingsAware(False)
    app = QtWidgets.QApplication(sys.argv)  # pylint: disable=invalid-name
    myapp = MainWindow("last_values.ini")
    myapp.show()
    sys.exit(app.exec_())
