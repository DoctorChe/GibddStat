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
import gibdd_stat_parser as gibdd


class MainWindow(QtWidgets.QMainWindow):
    """Основной класс программы"""

    def __init__(self, iniFile, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.updatecodes = False
        self.dir = "dtpdata"
        self.year = None
        self.month = None
        self.regcode = None

        # self.parser = gibdd.create_parser()
        # namespace = parser.parse_args(sys.argv[1:])
        # self.namespace = self.parser.parse_args(sys.argv[1:])

    def read_form_data(self):
        """Считывание данных с формы"""
        self.updatecodes = self.ui.checkBox_updatecodes.isChecked()
        # self.dir = "dtpdata"
        # Год
        try:
            self.year = int(self.ui.spinBox_year.value())
        except ValueError:
            msg = "Год введён не корректно."
            self.statusBar().showMessage(msg)
        # Месяц
        try:
            self.month = int(self.ui.spinBox_month.value())
        except ValueError:
            msg = "Месяц введён не корректно."
            self.statusBar().showMessage(msg)
        # Регион
        try:
            self.regcode = int(self.ui.spinBox_regcode.value())
        except ValueError:
            msg = "Регион введён не корректно."
            self.statusBar().showMessage(msg)

    def start_calculation(self):
        """Основная функция программы"""
        # pass
        # self.clear_results()  # Очистить данные предыдущих вычислений
        self.read_form_data()  # Считать данные с формы

        self.data_root = self.dir

        if not os.path.exists(self.data_root):
            os.makedirs(self.data_root)

        if not os.path.exists(gibdd.log_filename):
            gibdd.create_log()

        if self.updatecodes:
        # if self.updatecodes == "y":
            log_text = "Обновление справочника кодов регионов..."
            print(log_text)
            gibdd.write_log(log_text)
            gibdd.save_code_dictionary("regions.json")
            # log_text = "Обновление справочника завершено"
            # print(log_text)
            # gibdd.write_log(log_text)
        # elif self.updatecodes == "n":
        else:
            log_text = "Обновление справочника отменено"
            print(log_text)
            gibdd.write_log(log_text)

        # получаем год (если параметр опущен - текущий год)
        if self.year is not None:
            year = self.year
        else:
            year = datetime.now().year

        # получаем месяц (если параметр опущен - все прошедшие месяцы года)
        if self.month is not None:
            months = [int(self.month)]
        else:
            if year == str(datetime.now().year):
                months = list(range(1, datetime.now().month, 1))
            else:
                months = list(range(1, 13, 1))

        # загружаем данные из справочника ОКАТО-кодов регионов и муниципалитетов
        filename = "regions.json"
        with codecs.open(filename, "r", "utf-8") as f:
            regions = json.loads(json.loads(json.dumps(f.read())))

        # gibdd.get_dtp_info(self.data_root,
        #                    year,
        #                    months,
        #                    regions,
        #                    region_id=self.regcode)

        for region in regions:
            # была запрошена статистика по одному из регионов, а не по РФ
            if self.regcode != "0" and region["id"] == self.regcode:
                region_name = region["name"]
                break

        # Тест: читаем сохраненные данные ДТП
        path = os.path.join(self.data_root, year, f"{self.regcode} {region_name} {months[0]}-{months[-1]}.{year}.json")
        # with codecs.open(self.data_root + "\\" + str(year) + "\\41_3-3_2017.json", "r", encoding="utf-8") as f:
        with codecs.open(path, "r", encoding="utf-8") as f:
            json_content = json.loads(json.dumps(f.read()))
            print(json_content)


        # if not self.ga.rдопзм:
        #     self.statusBar().showMessage('Введите исходные данные.')
        #     dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
        #                                    "Сообщение",
        #                                    "Задайте нормируемое сопротивление растекания тока в землю",
        #                                    buttons=QtWidgets.QMessageBox.Ok,
        #                                    parent=self)
        #     dialog.exec()
        # elif not self.ga.Lв:
        #     self.statusBar().showMessage('Введите исходные данные.')
        #     dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
        #                                    "Сообщение",
        #                                    "Задайте высоту вертикального электрода",
        #                                    buttons=QtWidgets.QMessageBox.Ok,
        #                                    parent=self)
        #     dialog.exec()
        # else:
        #     try:
        #         self.ga.calc_R()
        #         if self.ga.mode:
        #             self.show_results_calc()
        #         else:
        #             self.show_results_check()
        #
        #     except ValueError:
        #         self.statusBar().showMessage('Введите исходные данные.')
        #     # except Exception:
        #     # Заглушка для всех ошибок
        #     #            print('Это что ещё такое?')
        #     else:
        #         msg = "Расчёт закончен успешно."
        #         self.statusBar().showMessage(msg)
        #     finally:
        #         # Выбирается вкладка "Результаты"
        #         if self.ui.radioButton.isChecked():
        #             self.ui.tabWidget.setCurrentWidget(self.ui.tab_calc_results)
        #         else:
        #             self.ui.tabWidget.setCurrentWidget(self.ui.tab_check_results)

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
