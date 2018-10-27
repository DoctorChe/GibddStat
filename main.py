#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Парсер сайта статистики ГИБДД для сбора и анализа данных"""

import sys
import os
from datetime import datetime
import json
import codecs
import re
from PyQt5 import QtWidgets
from PyQt5 import QtCore
# Импортируем наш интерфейс из файла
from ui.ui_mainwindow import Ui_MainWindow
import gibdd_stat_parser as gibdd


regions_json_filename = "regions.json"


class MainWindow(QtWidgets.QMainWindow):
    """Основной класс программы"""

    def __init__(self, iniFile, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.data_root = "dtpdata"
        self.year = ""
        self.month = ""
        self.regcode = ""

        self.ui.tableWidget.setHorizontalHeaderLabels(["Дата", "ДТП Район", "Вид ДТП", "Погибло", "Ранено",
                                                       "Кол-во ТС", "Кол-во уч."])

        # Установить текущий год
        self.ui.spinBox_year.setValue(datetime.now().year)

        # Установить список месяцев
        months = [""]
        months.extend([str(x) for x in range(1, 13)])
        self.ui.comboBox_month.insertItems(0, months)

        self.ui.comboBox_regcode.insertItems(0, self.get_combobox_regions())

    def get_combobox_regions(self):
        regions = self.read_regions_from_json()
        regions_dict = {}
        for region in regions:
            regions_dict[int(region['id'])] = region['name']
        regions_list = []
        for k, v in sorted(regions_dict.items()):
            regions_list.append(f"{k} - {v}")
        return regions_list

    def read_form_data(self):
        """Считывание данных с формы"""
        # self.data_root = "dtpdata"
        # Год
        try:
            self.year = str(self.ui.spinBox_year.value())
        except ValueError:
            msg = "Год введён не корректно."
            self.statusBar().showMessage(msg)
        # Месяц
        try:
            self.month = str(self.ui.comboBox_month.currentText())
        except ValueError:
            msg = "Месяц введён не корректно."
            self.statusBar().showMessage(msg)
        # Регион
        try:
            self.regcode = (re.match("([0-9]+) - (.*)", self.ui.comboBox_regcode.currentText())).group(1).strip()
        except ValueError:
            msg = "Регион введён не корректно."
            self.statusBar().showMessage(msg)

    def clear_results(self):
        self.ui.label_dtp_count.setText("0")
        self.ui.label_dead.setText("0")
        self.ui.label_inj.setText("0")
        self.ui.label_proc.setText("0.00%")
        # self.ui.tableWidget.setRowCount(0)
        for row in reversed(range(self.ui.tableWidget.rowCount())):
            self.ui.tableWidget.removeRow(row)

    def start_calculation(self):
        """Основная функция программы"""
        # pass
        self.clear_results()  # Очистить данные предыдущих вычислений
        self.read_form_data()  # Считать данные с формы

        if not os.path.exists(self.data_root):
            os.makedirs(self.data_root)

        if not os.path.exists(gibdd.log_filename):
            gibdd.create_log()

        # # получаем год (если параметр опущен - текущий год)
        # if self.year is not None:
        #     year = self.year
        # else:
        #     year = datetime.now().year

        # получаем месяц (если параметр опущен - все прошедшие месяцы года)
        # if self.month is not None and self.month != "":
        if self.month:
            months = [int(self.month)]
        else:
            if self.year == str(datetime.now().year):
                months = list(range(1, datetime.now().month, 1))
            else:
                months = list(range(1, 13, 1))

        # загружаем данные из справочника ОКАТО-кодов регионов и муниципалитетов
        regions = self.read_regions_from_json()

        gibdd.get_dtp_info(self.data_root,
                           self.year,
                           months,
                           regions,
                           region_id=self.regcode)

        # Тест: читаем сохраненные данные ДТП
        for region in regions:
            if self.regcode != "0" and region["id"] == self.regcode:
                region_name = region["name"]
                break
        path = os.path.join(self.data_root,
                            self.year,
                            f"{self.regcode} {region_name} {months[0]}-{months[-1]}.{year}.json")
        dtp_data = gibdd.read_dtp_data(path)

        self.ui.label_dtp_count.setText(dtp_data["dtp_count"])
        self.ui.label_dead.setText(dtp_data["pog"])
        self.ui.label_inj.setText(dtp_data["ran"])
        self.ui.label_proc.setText(dtp_data["proc"])

        for dtp in dtp_data["dtp_data"].values():
            row_position = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row_position)  # insert new row
            # self.ui.tableWidget.setItem(row_position-1, 0, QtWidgets.QTableWidgetItem(dtp["index"]))
            self.ui.tableWidget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(dtp["date"]))
            self.ui.tableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(dtp["District"]))
            self.ui.tableWidget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(dtp["DTP_V"])))
            self.ui.tableWidget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(dtp["POG"])))
            self.ui.tableWidget.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(dtp["RAN"])))
            self.ui.tableWidget.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(dtp["K_TS"])))
            self.ui.tableWidget.setItem(row_position, 6, QtWidgets.QTableWidgetItem(str(dtp["K_UCH"])))

        self.ui.tableWidget.setSortingEnabled(True)
        self.ui.tableWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.tableWidget.resizeColumnsToContents()

        self.ui.groupBox_2.setTitle(f"Статистика по региону: {region_name}")

    @staticmethod
    def read_regions_from_json():
        with codecs.open(regions_json_filename, "r", "utf-8") as f:
            regions = json.loads(json.loads(json.dumps(f.read())))
        return regions

    @QtCore.pyqtSlot()
    # def update_codes(self, regions_json_filename):
    def update_codes(self):
        log_text = "Обновление справочника кодов регионов..."
        print(log_text)
        self.ui.statusbar.showMessage(log_text)
        gibdd.write_log(log_text)
        gibdd.save_code_dictionary(regions_json_filename)
        log_text = "Обновление справочника завершено"
        print(log_text)
        self.ui.statusbar.showMessage(log_text)
        gibdd.write_log(log_text)

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
