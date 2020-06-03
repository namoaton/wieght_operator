import os
import sys
import tempfile

os.chdir(os.path.dirname(__file__))

from threading import Lock, Thread
# import serial
from Weight_tools.Car import AddCar
from Weight_tools.Kassir import KassiryWindows, DodatyKassira, RemoveKassir
from Weight_tools.MyDictionaryCompleter import MyDictionaryCompleter
from Weight_tools.Record import Record
from Weight_tools.Record import *
from Weight_tools.WeightThread import ReadWeightThread, EditThread
from Weight_tools.tools import *
from Weight_tools.Postachalnik import DodatyPostachalnika, PostachalnikiWindows, RemovePostachalnik, PostachEditRecord
from Weight_tools.DateDialog import *
from Weight_tools.WaitEditor import EditWaitForArchive

# import win32api
# import win32print
import paho.mqtt.client as mqtt
from PyQt5 import QtCore, QtGui, QtWidgets

# print(serial.VERSION)
# serialport = serial.Serial('COM5')
# serialport.baudrate = 9600
# serialport.startbit = 1
# serialport.timeout = 5
# serialport.stopbit = 1

configParser = configparser.RawConfigParser()
configFilePath = "Weight_tools/weight.conf"
configParser.read(configFilePath)

MQTT_USER = configParser.get('CONFIG', 'MQTT_USER')
MQTT_PASSWORD = configParser.get('CONFIG', 'MQTT_PASSWORD')
MQTT_CLIENT = configParser.get('CONFIG', 'MQTT_CLIENT')

mqtt_client = mqtt.Client(MQTT_CLIENT)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.connect(host, port=1883, keepalive=60)
comm = Communicate()

threadLock = Lock()
threads = []


class MainWindow(QtWidgets.QMainWindow):
    # procDone = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        # creating EmailBlast widget and setting it as central
        self.window_widget = Window(parent=self)
        self.setCentralWidget(self.window_widget)
        self.setWindowTitle("ВінМакулатура")
        self.setWindowIcon(QtGui.QIcon(os.path.realpath(__file__).replace("wieght.py", "") + 'recycling.png'))
        print(os.path.realpath(__file__))
        # filling up a menu bar
        self.menubar = self.menuBar()
        # self.menu =  QtWidgets.QMenu(self.menubar)
        self.postach_menu = self.menubar.addMenu('Постачальники')
        self.kassir_menu = self.menubar.addMenu('Касири')
        self.report_menu = self.menubar.addMenu('Звіти')
        self.our_cars_menu = self.menubar.addMenu('Наші авто')
        self.record_edit_menu = self.menubar.addMenu('Записи')

        self.record_editor_menu = QtWidgets.QAction('Друк документа', self)
        self.record_editor_menu.triggered.connect(self.edit_record)
        self.record_adder_menu = QtWidgets.QAction('Введення документа', self)
        self.record_adder_menu.triggered.connect(self.add_record)
        self.record_remove_menu = QtWidgets.QAction('Видалити документ', self)
        self.record_remove_menu.triggered.connect(self.remove_record)
        self.record_postach_edit_menu = QtWidgets.QAction('Редагувати постачальника в документі', self)
        self.record_postach_edit_menu.triggered.connect(self.postach_edit_record)

        respond = make_request("SELECT dozvol from `dozvol` WHERE id=1")
        if respond[0][0] == 0:
            self.record_allow_menu = QtWidgets.QAction('Дозволити введення ',
                                                       self)
        else:
            self.record_allow_menu = QtWidgets.QAction('Заборонити введення ',
                                                       self)
        self.record_allow_menu.triggered.connect(self.allow_record)
        self.record_edit_menu.addAction(self.record_allow_menu)

        self.record_return_menu = QtWidgets.QAction('Повернення документа',
                                                    self)
        self.record_return_menu.triggered.connect(self.return_record)

        self.record_edit_menu.addAction(self.record_editor_menu)
        self.record_edit_menu.addAction(self.record_adder_menu)
        self.record_edit_menu.addAction(self.record_return_menu)
        self.record_edit_menu.addAction(self.record_remove_menu)
        self.record_edit_menu.addAction(self.record_postach_edit_menu)
        self.list_postach_menu = QtWidgets.QMenu('Перелік постачальників',
                                                 self)
        self.remove_postach_menu = QtWidgets.QAction('Видалити постачальника', self)
        self.remove_postach_menu.triggered.connect(self.remove_postach)
        self.list_postach_action = QtWidgets.QAction('Дивитися', self)
        self.add_postach_to_list = QtWidgets.QAction('Додати', self)
        self.list_postach_action.triggered.connect(self.show_postach)
        self.add_postach_to_list.triggered.connect(self.add_postach)
        self.list_postach_menu.addAction(self.list_postach_action)
        self.list_postach_menu.addAction(self.add_postach_to_list)
        self.postach_menu.addAction(self.remove_postach_menu)
        self.show_kassir_menu = QtWidgets.QAction('Перелік касирів', self)
        self.add_kassir = QtWidgets.QAction('Додати касира', self)
        self.remove_kassir_menu = QtWidgets.QAction('Видалити касира', self)
        self.show_kassir_menu.triggered.connect(self.show_kassir)
        self.add_kassir.triggered.connect(self.add_kassiry)
        self.remove_kassir_menu.triggered.connect(self.remove_kassir)
        self.kassir_menu.addAction(self.show_kassir_menu)
        self.kassir_menu.addAction(self.add_kassir)
        self.kassir_menu.addAction(self.remove_kassir_menu)
        # self.today_report_menu = QtWidgets.QAction('Отчет за сегодня')
        self.date_report_menu = QtWidgets.QAction('Звіт загальний по даті')
        self.month_report_menu = QtWidgets.QAction('Звіт загальний за період')
        self.date_report_bn_menu = QtWidgets.QAction('Звіт безнал по даті')
        self.month_report_bn_menu = QtWidgets.QAction('Звіт безнал за період')
        self.date_report_pr_menu = QtWidgets.QAction('Звіт готівка по даті')
        self.month_report_pr_menu = QtWidgets.QAction('Звіт готівка за період')

        self.date_report_makul_bn_menu = QtWidgets.QAction(
            'Звіт макулатра бн по даті')
        self.month_report_makul_bn_menu = QtWidgets.QAction(
            'Звіт макулатра бн за період')
        self.date_report_polymer_bn_menu = QtWidgets.QAction(
            'Звіт полімери бн по даті')
        self.month_report_polymer_bn_menu = QtWidgets.QAction(
            'Звіт полімери бн за період')
        # self.today_report_menu.triggered.connect(self.today_report)
        self.date_report_menu.triggered.connect(self.date_report)
        self.month_report_menu.triggered.connect(self.month_report)

        self.date_report_bn_menu.triggered.connect(self.date_report_bn)
        self.month_report_bn_menu.triggered.connect(self.month_report_bn)

        self.date_report_pr_menu.triggered.connect(self.date_report_pr)
        self.month_report_pr_menu.triggered.connect(self.month_report_pr)

        self.date_report_makul_bn_menu.triggered.connect(
            self.date_mak_bn_report)
        self.month_report_makul_bn_menu.triggered.connect(
            self.period_mak_bn_report)
        self.date_report_polymer_bn_menu.triggered.connect(
            self.date_pol_bn_report)
        self.month_report_polymer_bn_menu.triggered.connect(
            self.period_pol_bn_report)

        # self.report_menu.addAction(self.today_report_menu)
        self.report_menu.addAction(self.date_report_menu)
        self.report_menu.addAction(self.month_report_menu)
        self.report_menu.addAction(self.date_report_bn_menu)
        self.report_menu.addAction(self.month_report_bn_menu)
        self.report_menu.addAction(self.date_report_pr_menu)
        self.report_menu.addAction(self.month_report_pr_menu)

        self.report_menu.addAction(self.date_report_makul_bn_menu)
        self.report_menu.addAction(self.month_report_makul_bn_menu)
        self.report_menu.addAction(self.date_report_polymer_bn_menu)
        self.report_menu.addAction(self.month_report_polymer_bn_menu)

        self.postach_menu.addMenu(self.list_postach_menu)
        self.add_out_cars_menu = QtWidgets.QAction('Додати наше авто')
        self.add_out_cars_menu.triggered.connect(self.add_car)
        self.our_cars_menu.addAction(self.add_out_cars_menu)
        self.dialog = PostachalnikiWindows(self)
        self.dodatyPostachalnika = DodatyPostachalnika(self)
        self.dodatyKassira = DodatyKassira(self)
        self.removeKassir = RemoveKassir(self)
        self.kassiryWindows = KassiryWindows(self)
        self.dateDialog = DateDialog()
        self.doubleDateDialog = DoubleDateDialog()
        self.addCar = AddCar(self)
        self.record_editor = RecordSelector()
        self.ret_record = ReturnRecord()
        self.rem_record = RemoveRecord()
        self.edit_postach = PostachEditRecord()
        self.removePostach = RemovePostachalnik()
        # self.lcd_signal.emit(str(message.payload.decode("utf-8")))

    def date_mak_bn_report(self):
        date, time, ok = self.dateDialog.getDateTime()
        query = "SELECT * FROM records WHERE DATE(date) ='%s' AND is_finished = 1 AND is_archived = 1 AND ( " % '{0:%Y-%m-%d}'.format(
            date)
        for m in makulatura:
            query = query + "material LIKE ('%" + m + "%') OR "
        query = query[:-3]
        query = query + ")"
        result = make_request(query)
        if ok:
            # print(query)
            DisplayRecords(self, result, date, bn=1).show()

    def period_mak_bn_report(self):
        end_date, end_time, begin_date, begin_time, ok = self.doubleDateDialog.getDateTime(
        )
        query = "SELECT * FROM records WHERE DATE(date) >='%s' and DATE(date)<='%s' AND is_finished = 1 AND is_archived = 1 AND (" % (
        '{0:%Y-%m-%d}'.format(end_date),
        '{0:%Y-%m-%d}'.format(begin_date))
        for m in makulatura:
            query = query + "material LIKE ('%" + m + "%') OR "
        query = query[:-3]
        query = query + ")"
        result = make_request(query)
        if ok:
            DisplayRecords(self, result, begin_date, end_date, bn=1).show()

    def date_pol_bn_report(self):
        date, time, ok = self.dateDialog.getDateTime()
        query = "SELECT * FROM records WHERE DATE(date) ='%s' AND is_finished = 1 AND is_archived = 1 AND  ( " % '{0:%Y-%m-%d}'.format(
            date)
        for p in polymer:
            query = query + "material LIKE ('%" + p + "%') OR "
        query = query[:-3]
        query = query + ")"
        result = make_request(query)
        if ok:
            # print(query)
            DisplayRecords(self, result, date, bn=2).show()

    def period_pol_bn_report(self):
        end_date, end_time, begin_date, begin_time, ok = self.doubleDateDialog.getDateTime(
        )
        query = "SELECT * FROM records WHERE DATE(date) >='%s' and DATE(date)<='%s' AND is_finished = 1 AND is_archived = 1 AND (" % (
        '{0:%Y-%m-%d}'.format(end_date),
        '{0:%Y-%m-%d}'.format(begin_date))
        for p in polymer:
            query = query + "material LIKE ('%" + p + "%') OR "
        query = query[:-3]
        query = query + ")"
        result = make_request(query)
        if ok:
            DisplayRecords(self, result, begin_date, end_date, bn=2).show()

    def return_record(self):
        print("return record")
        self.ret_record.show()

    def remove_record(self):
        print("remove record")
        self.rem_record.show()

    def postach_edit_record(self):
        self.edit_postach.show()

    def remove_postach(self):
        self.removePostach.show()

    def allow_record(self):
        respond = make_request("SELECT dozvol from `dozvol` WHERE id=1")
        flag = 0
        if respond[0][0] == 0:
            flag = 1
            self.record_allow_menu.setText('Заборонити введення документів')
        else:
            flag = 0
            self.record_allow_menu.setText('Дозволити введення документів')
        write_to_db("UPDATE `dozvol` SET dozvol=%d WHERE id=1" % flag)

    def edit_record(self):
        id_rec = self.record_editor.getRecordID()
        print(id_rec)
        self.editor_record_window = RecordEditor(self, id_rec)
        self.editor_record_window.show()

    def add_record(self):
        print("NEW RECORD")
        self.add_record_window = AddRecord(self)
        self.add_record_window.show()
        # self.editor_record_window = RecordEditor(self, id_rec)
        # self.editor_record_window.show()

    def add_car(self):
        self.addCar.procDone.connect(self.window_widget.our_cars_reload)
        self.addCar.show()

    def show_postach(self):
        self.dialog.show()

    def add_postach(self):
        self.dodatyPostachalnika.show()

    def show_kassir(self):
        self.kassiryWindows.show()

    def add_kassiry(self):
        self.dodatyKassira.show()

    def remove_kassir(self):
        self.removeKassir.show()

    def today_report(self):
        self.todayRecords.show()

    def month_report(self):
        end_date, end_time, begin_date, begin_time, ok = self.doubleDateDialog.getDateTime(
        )
        result = make_request(
            "SELECT * FROM records WHERE DATE(date) >='%s' and DATE(date)<='%s' AND is_finished = 1 AND is_archived = 1"
            % ('{0:%Y-%m-%d}'.format(end_date),
               '{0:%Y-%m-%d}'.format(begin_date)))
        if ok:
            DisplayRecords(self, result, begin_date, end_date).show()

    def date_report(self):
        date, time, ok = self.dateDialog.getDateTime()
        result = make_request(
            "SELECT * FROM records WHERE DATE(date) ='%s' AND is_finished = 1 AND is_archived = 1"
            % '{0:%Y-%m-%d}'.format(date))
        if ok:
            DisplayRecords(self, result, date).show()

    def month_report_bn(self):
        end_date, end_time, begin_date, begin_time, ok = self.doubleDateDialog.getDateTime(
        )
        result = make_request(
            "SELECT * FROM records WHERE DATE(date) >='%s' and DATE(date)<='%s' AND is_finished = 1 AND is_archived = 1 AND material LIKE ('%s')"
            % ('{0:%Y-%m-%d}'.format(end_date),
               '{0:%Y-%m-%d}'.format(begin_date), "%-бн%"))
        if ok:
            DisplayRecords(self, result, begin_date, end_date, bn=3).show()

    def date_report_bn(self):
        date, time, ok = self.dateDialog.getDateTime()
        result = make_request(
            "SELECT * FROM records WHERE DATE(date) ='%s' AND is_finished = 1 AND is_archived = 1 AND material LIKE ('%s')"
            % ('{0:%Y-%m-%d}'.format(date), "%-бн%"))
        if ok:
            DisplayRecords(self, result, date, bn=3).show()

    def month_report_pr(self):
        end_date, end_time, begin_date, begin_time, ok = self.doubleDateDialog.getDateTime(
        )
        result = make_request(
            "SELECT * FROM records WHERE DATE(date) >='%s' and DATE(date)<='%s' AND is_finished = 1 AND is_archived = 1 AND material NOT LIKE ('%s')"
            % ('{0:%Y-%m-%d}'.format(end_date),
               '{0:%Y-%m-%d}'.format(begin_date), "%-бн%"))
        if ok:
            DisplayRecords(self, result, begin_date, end_date, bn=4).show()

    def date_report_pr(self):
        date, time, ok = self.dateDialog.getDateTime()
        result = make_request(
            "SELECT * FROM records WHERE DATE(date) ='%s' AND is_finished = 1 AND is_archived = 1 AND material NOT LIKE ('%s')"
            % ('{0:%Y-%m-%d}'.format(date), "%-бн%"))
        if ok:
            DisplayRecords(self, result, date, bn=4).show()


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        global postachalnik_list
        self.newfont = QtGui.QFont("Arial", 24, QtGui.QFont.Bold)
        self.active_kassir = kassiry[0]
        self.car_num_label = QtWidgets.QLabel('Номер авто')
        self.car_num_label.setFont(self.newfont)
        self.car_num = QtWidgets.QLineEdit()
        self.car_num.setFont(self.newfont)
        self.car_num.setFixedWidth(350)
        self.price_label = QtWidgets.QLabel('Ціна')
        self.price_label.setFont(self.newfont)
        # TODO make integer checking function
        self.price = QtWidgets.QLineEdit()
        self.price.setFont(self.newfont)
        self.price.setFixedWidth(350)
        self.price.setText("0")
        # self.weight = QtWidgets.QLabel()
        self.weight = QtWidgets.QLCDNumber(self)
        print(self.weight.height())
        self.weight.setFixedHeight(100)
        # self.weight.display(str(500))
        get_kassiry()
        self.kassir = QtWidgets.QComboBox()
        self.kassir.setFont(self.newfont)
        self.kassir.addItems(kassiry)
        self.kassir.setFixedWidth(350)
        self.kassir_label = QtWidgets.QLabel('Касир')
        self.kassir_label.setFont(self.newfont)
        self.material_label = QtWidgets.QLabel('Сировина')
        self.material_label.setFont(self.newfont)
        # self.material = QtWidgets.QComboBox()
        self.material = QtWidgets.QLineEdit()
        self.material.setFixedWidth(350)
        self.material.setFont(self.newfont)
        self.material_completer = QtWidgets.QCompleter(materials)
        self.material_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.material.setCompleter(self.material_completer)
        # self.material.addItems(materials)
        self.get_weight_button = QtWidgets.QPushButton('Отримати вагу')
        self.get_weight_button.setFont(self.newfont)
        self.write_button = QtWidgets.QPushButton('Записати')
        self.write_button.setFont(self.newfont)
        self.entrance_checkbox = QtWidgets.QCheckBox("В'їзд")
        self.entrance_checkbox.setFont(self.newfont)

        self.rashod_checkbox = QtWidgets.QCheckBox("Видача")
        self.rashod_checkbox.setFont(self.newfont)
        # self.entrance_checkbox.toggle()
        # self.pay_checkbox = QtWidgets.QCheckBox('Сплачено')
        # self.pay_checkbox.setFont(self.newfont)
        self.pending_car_list = QtWidgets.QListWidget()
        self.listfont = QtGui.QFont("Times", 17, QtGui.QFont.Normal)
        self.pending_car_list.setFont(self.listfont)
        self.pending_car_list.addItems(car_list)
        # self.topframe = QtWidgets.QFrame(self)
        # self.topframe.setLineWidth(2)
        # self.topframe.setFrameShape(QtWidgets.QFrame.WinPanel)
        # self.topframe.setFrameShadow(QtWidgets.QFrame.Raised)
        # self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        # self.splitter.setHandleWidth(1)
        # self.splitter.addWidget(self.topframe)
        self.pending_car_label = QtWidgets.QLabel('Авто на розвантаженні')
        self.pending_car_label.setFont(self.newfont)
        self.pending_car_label.setStyleSheet(
            "color: black;border-style: groove;border-width: 1px; border-color: #a6a7a8")
        self.postachalnik_label = QtWidgets.QLabel("Постачальник")
        self.zasor_label = QtWidgets.QLabel("Засмічення")
        self.zasor_label.setFont(self.newfont)
        self.zasor = QtWidgets.QLineEdit()
        self.zasor.setFont(self.newfont)
        self.zasor.setFixedWidth(350)
        self.zasor.setText("0")
        # self.material_table = QtWidgets.QTableWidget()
        # self.material_table.setSizeAdjustPolicy(
        #     QtWidgets.QAbstractScrollArea.AdjustToContents)
        # self.material_table.setColumnCount(2)
        # self.material_table.setRowCount(0)
        # self.material_table.setHorizontalHeaderLabels(["Сировина", "Вага"])
        # self.material_table.resizeColumnsToContents()
        # self.material_table.resizeRowsToContents()
        # self.material_header = self.material_table.horizontalHeader()
        # # self.material_header.setResizeMode(QHeaderView.ResizeToContents)
        # self.material_header.setSectionResizeMode(
        #     QtWidgets.QHeaderView.Stretch)
        # self.material_header.setStretchLastSection(True)
        get_postachalniky()
        self.postachalnik_label.setFont(self.newfont)
        self.postachalnik_completer = QtWidgets.QCompleter(postachalnik_list)
        self.postachalnik_completer.setCaseSensitivity(
            QtCore.Qt.CaseInsensitive)
        self.postachalnik = QtWidgets.QLineEdit()  # QtWidgets.QComboBox()
        self.postachalnik.setFixedWidth(350)
        self.postachalnik.setFont(self.newfont)
        self.postachalnik.setCompleter(self.postachalnik_completer)

        # NO Archive
        self.wait_for_archive_label = QtWidgets.QLabel(
            'Записи до підтверждення')
        self.wait_for_archive_label.setFont(self.newfont)
        self.wait_for_archive_button = QtWidgets.QPushButton('Оновити')

        self.wait_for_archive_table = QtWidgets.QTableWidget()
        self.wait_for_archive_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.wait_table_header = [
            "Номер запису", "Дата", "Постачальник", "№ Авто"
        ]
        self.wait_for_archive_table.setColumnCount(len(self.wait_table_header))
        self.wait_for_archive_table.setRowCount(0)
        self.wait_for_archive_table.setHorizontalHeaderLabels(
            self.wait_table_header)
        for i in range(len(self.wait_table_header)):
            self.wait_for_archive_table.horizontalHeaderItem(i).setToolTip(
                self.wait_table_header[i])
            self.wait_for_archive_table.horizontalHeaderItem(
                i).setTextAlignment(QtCore.Qt.AlignLeft)
        self.wait_for_archive_table.resizeColumnsToContents()
        self.wait_for_archive_table.resizeRowsToContents()
        self.wait_for_archive_header = self.wait_for_archive_table.horizontalHeader(
        )
        # self.material_header.setResizeMode(QHeaderView.ResizeToContents)
        self.wait_for_archive_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.wait_for_archive_header.setStretchLastSection(True)
        # fill wait for archive
        counter = 0
        row_index = 0
        for i in wait_for_archive_list:
            print(len(i))
            self.wait_for_archive_table.insertRow(row_index)
            self.wait_for_archive_table.setItem(row_index, 0,
                                                QtWidgets.QTableWidgetItem(
                                                    str(i[14])))
            self.wait_for_archive_table.setItem(
                row_index, 1,
                QtWidgets.QTableWidgetItem('{0:%d-%m-%Y %H:%M:%S}'.format(
                    i[0])))
            self.wait_for_archive_table.setItem(row_index, 2,
                                                QtWidgets.QTableWidgetItem(
                                                    i[5]))
            self.wait_for_archive_table.setItem(row_index, 3,
                                                QtWidgets.QTableWidgetItem(
                                                    i[1]))
            row_index = row_index + 1
        self.our_cars_label = QtWidgets.QLabel('Наші авто')
        self.our_cars_reload_button = QtWidgets.QPushButton('Оновити перелік')
        self.car_newfont = QtGui.QFont("Times", 14)
        self.wait_for_archive_button.setFont(self.car_newfont)
        self.our_cars_label.setFont(self.newfont)
        self.our_cars = QtWidgets.QListWidget()
        self.our_cars.setFont(self.car_newfont)
        self.our_cars.addItems(our_cars_list)
        # self.pay_checkbox.toggle()
        cb_box = QtWidgets.QHBoxLayout()
        cb_box.addWidget(self.entrance_checkbox)
        cb_box.addWidget(self.rashod_checkbox)
        # cb_box.addWidget(self.pay_checkbox)
        price_box = QtWidgets.QHBoxLayout()
        # price_box.addStretch()
        # price_box.addWidget(self.price_label)
        # price_box.addWidget(self.price)
        car_num_box = QtWidgets.QHBoxLayout()
        # car_num_box.addStretch()
        car_num_box.addWidget(self.car_num_label)
        car_num_box.addWidget(self.car_num)
        postach_box = QtWidgets.QHBoxLayout()
        postach_box.addWidget(self.postachalnik_label)
        postach_box.addWidget(self.postachalnik)
        zasor_box = QtWidgets.QHBoxLayout()
        # zasor_box.addWidget(self.zasor_label)
        # zasor_box.addWidget(self.zasor)
        v_box = QtWidgets.QVBoxLayout()
        v_box.addLayout(car_num_box)
        # v_box.addLayout(price_box)
        v_box.addLayout(postach_box)
        # v_box.addLayout(zasor_box)
        # v_box.addWidget(self.splitter)
        v_box.addWidget(self.pending_car_label)
        v_box.addWidget(self.pending_car_list)
        # v_box.addWidget(self.material_table)
        v_box.addStretch()
        # v_box.addWidget(self.pending_car_list)
        v_box.addLayout(cb_box)
        kassir_hbox = QtWidgets.QHBoxLayout()
        kassir_hbox.addWidget(self.kassir_label)
        kassir_hbox.addWidget(self.kassir)
        material_hbox = QtWidgets.QHBoxLayout()
        # material_hbox.addWidget(self.material_label)
        # material_hbox.addWidget(self.material)
        v_box.addWidget(self.weight)
        v_box.addLayout(kassir_hbox)
        v_box.addLayout(material_hbox)
        h_box = QtWidgets.QHBoxLayout()
        # h_box.addStretch()
        # h_box.addWidget(self.get_weight_button)
        h_box.addWidget(self.write_button)
        v_box.addLayout(h_box)

        # self.topframe.addLayout(v_box)

        pending_box = QtWidgets.QHBoxLayout()
        pending_box.addLayout(v_box)
        pending_vbox = QtWidgets.QVBoxLayout()
        pending_vbox.addWidget(self.wait_for_archive_label)
        pending_vbox.addWidget(self.wait_for_archive_table)
        pending_vbox.addWidget(self.wait_for_archive_button)
        pending_vbox.addWidget(self.our_cars_label)
        # pending_vbox.addWidget(self.our_cars_reload_button)
        pending_vbox.addWidget(self.our_cars)
        pending_box.addLayout(pending_vbox)
        # self.setLayout(v_box)
        self.setLayout(pending_box)
        self.setWindowTitle('ВАГИ 1.0')
        self.setGeometry(300, 300, 300, 200)
        self.kassir.activated.connect(self.onActivated)
        # self.material.activated.connect(self.onMaterialActivated)
        # self.get_weight_button.clicked.connect(self.get_weight)
        self.write_button.clicked.connect(self.write_data)
        self.entrance_checkbox.stateChanged.connect(self.setEntrance)
        # self.pay_checkbox.stateChanged.connect(self.setPayment)
        self.pending_car_list.itemDoubleClicked.connect(self.fillData)
        self.our_cars.itemDoubleClicked.connect(self.fillOurData)
        self.our_cars_reload_button.clicked.connect(self.our_cars_reload)
        self.material.returnPressed.connect(self.materialEnterClicked)
        self.wait_for_archive_button.clicked.connect(self.reload_archive)
        self.wait_for_archive_table.itemDoubleClicked.connect(self.archiveEdit)
        self.record = Record()
        ReadWeightThread(self.weight)
        global comm
        comm.set(self.reload_all)
        Record.comm = comm
        self.reload_all()
        # EditThread(self.wait_for_archive_table)

    def update_completer_postach(self):
        global postachalnik_list
        get_postachalniky()
        self.postachalnik_completer = QtWidgets.QCompleter(postachalnik_list)
        self.postachalnik_completer.setCaseSensitivity(
            QtCore.Qt.CaseInsensitive)
        self.postachalnik.setCompleter(self.postachalnik_completer)

    def reload_all(self):
        self.reload_pending()
        self.reload_archive()
        self.our_cars_reload()
        self.reload_kassiry()
        self.update_completer_postach()
        # postachalnik_list=[]
        # result = make_request("SELECT * FROM postachalniky")
        # for i in result:
        #     postachalnik_list.append(i[0].lower())

    def reload_kassiry(self):
        global kassiry
        get_kassiry()
        self.kassir.clear()  # delete all items from comboBox
        self.kassir.addItems(kassiry)

    def archiveEdit(self):
        print("Achive clicked")
        row = self.wait_for_archive_table.selectedIndexes()[0].row()
        print(row)
        index = self.wait_for_archive_table.item(row, 0).text()
        result = make_request("SELECT * FROM records WHERE id =%s" % index)
        archEdit = EditWaitForArchive(self, index, result)
        archEdit.procDone.connect(self.reload_archive)
        archEdit.show()
        # self.completed.connect(self.reload_archive)

    def reload_pending(self):
        print("reload_pending")
        self.pending_car_list.clear()
        car_list = []
        result = make_request("SELECT * FROM records WHERE is_finished = 0")
        row_index = 0
        color = IN_COLOR
        sign = IN_SIGN
        for i in result:
            car_list.append(i[1])
            if i[16]:
                color = OUT_COLOR
                sign = OUT_SIGN
            else:
                color = IN_COLOR
                sign = IN_SIGN
            self.pending_car_list.addItem(i[1])
            self.pending_car_list.item(row_index).setBackground(color)
            row_index = row_index + 1

        # print(car_list)
        # self.pending_car_list.addItems(car_list)

    # @QtCore.pyqtSlot(str)
    def reload_archive(self):
        # print("CLose archive windows")
        print('Get waiting records')
        self.reload_pending()
        wait_for_archive_list = make_request(
            "SELECT * FROM records WHERE is_archived = 0 AND is_finished = 1")
        print(wait_for_archive_list)
        self.wait_for_archive_table.setRowCount(0)
        row_index = 0
        color = IN_COLOR
        for i in wait_for_archive_list:
            print(len(i))
            self.wait_for_archive_table.insertRow(row_index)
            self.wait_for_archive_table.setItem(row_index, 0,
                                                QtWidgets.QTableWidgetItem(
                                                    str(i[14])))
            self.wait_for_archive_table.setItem(
                row_index, 1,
                QtWidgets.QTableWidgetItem('{0:%d-%m-%Y %H:%M:%S}'.format(
                    i[0])))
            self.wait_for_archive_table.setItem(row_index, 2,
                                                QtWidgets.QTableWidgetItem(
                                                    i[5]))
            self.wait_for_archive_table.setItem(row_index, 3,
                                                QtWidgets.QTableWidgetItem(
                                                    i[1]))
            if i[16]:
                color = OUT_COLOR
                sign = OUT_SIGN
            else:
                color = IN_COLOR
                sign = IN_SIGN
            self.wait_for_archive_table.item(row_index, 0).setBackground(color)
            self.wait_for_archive_table.item(row_index, 1).setBackground(color)
            self.wait_for_archive_table.item(row_index, 2).setBackground(color)
            self.wait_for_archive_table.item(row_index, 3).setBackground(color)
            row_index = row_index + 1

    def materialEnterClicked(self):
        rowPosition = self.material_table.rowCount()
        mater = self.material.text()
        self.materials_json_value = {}
        total_rows = self.material_table.rowCount()
        print("total_rows = ", total_rows)
        if total_rows > 0:
            for i in range(0, total_rows):
                if mater == self.material_table.item(i, 0).text():
                    self.material_table.setItem(
                        i, 1,
                        QtWidgets.QTableWidgetItem(
                            str(self.weight.intValue())))
                    print("уже есть в таблице")
                    return
        self.material_table.insertRow(rowPosition)
        self.material_table.setItem(rowPosition, 0,
                                    QtWidgets.QTableWidgetItem(mater))
        self.material_table.setItem(rowPosition, 1,
                                    QtWidgets.QTableWidgetItem(
                                        str(self.weight.intValue())))
        self.material.clear()

    def our_cars_reload(self):
        result = make_request("SELECT * FROM our_car")
        self.our_cars.clear()
        del our_cars_list[:]
        for i in result:
            our_cars_list.append(i[1].lower())
            print(i[1])
        self.our_cars.addItems(our_cars_list)

    def fillOurData(self, index):
        num = self.our_cars.currentItem().text()
        print(num)
        try:
            self.car_num.setText(num)
            # self.postachalnik.setText("Вінмакулатура")
            self.postachalnik.setText("")
        except Exception as e:
            print('Error')

    def get_print_string(self, diff_time_str, data):
        if self.rashod_checkbox.isChecked():
            brutto = self.record.tara
            tara = self.record.brutto
        else:
            brutto = self.record.brutto
            tara = self.record.tara
        self.record.netto = brutto - tara
        printstring = "+ Касир : %s\n+ Номер авто: %s\n+ Постачальник: %s\n+ Матеріал: %s\n+ Брутто: %d кг\n+ Тара: %d кг\n+ Нетто: %d кг\n+ Засмічення в кг: %d \n+ Ціна за кг: %.2f\n+ До сплати(грн): %.2f\n+ Дата: %s\n+ Час розвантаження: %s\n" % (
            self.record.kassir,
            self.record.avto,
            self.record.postachalnik,
            self.record.material,
            brutto,
            tara,
            self.record.netto,
            self.record.zasor,
            self.record.price,
            (self.record.netto * self.record.
             price) - self.record.zasor, data,
            diff_time_str)
        return printstring

    def get_enter_time(self):
        result = make_request(
            "SELECT * FROM records WHERE car_num ='%s' AND is_finished = 0"
            % self.record.avto)
        if len(result) == 0:
            return None
        return result[0][0]

    def update_entrance_record_by_kassir(self):
        query = "UPDATE records SET tara = %d, is_enter = %d, is_oplacheno = %d ,is_finished = %d, exit_time=now(), netto = %d, zasor = %d WHERE car_num = '%s'   AND is_finished = 0 " % (
            self.record.vaga,
            self.record.is_enter,
            self.record.is_oplacheno,
            self.record.if_finished,
            self.record.netto,
            self.record.zasor,
            self.record.avto)
        print(query)
        write_to_db(query)

    def confirm_window(self, weight_before):
        kassir_question = QtWidgets.QMessageBox()
        kassir_question.setIcon(
            QtWidgets.QMessageBox.Question)
        kassir_question.setWindowTitle("Записати?")
        dialogfont = QtGui.QFont(
            "Times", 17, QtGui.QFont.Normal)
        kassir_question.setFont(dialogfont)

        result = make_request("SELECT now()")
        exit_time = result[0][0]
        enter_time = self.get_enter_time()
        if enter_time == None:
            return
        diff_time = exit_time - enter_time
        print(diff_time)
        if self.rashod_checkbox.isChecked():
            vaga = self.record.vaga - weight_before
        else:
            vaga = weight_before - self.record.vaga
        data = '{0:%Y-%m-%d %H:%M:%S}'.format(
            datetime.datetime.now())
        diff_time_str = str(diff_time)
        printstring = self.get_print_string(diff_time_str, data)

        kassir_question.setText(printstring)
        kassir_question.setStandardButtons(
            QtWidgets.QMessageBox.Yes
            | QtWidgets.QMessageBox.No)
        printButton = kassir_question.addButton(
            'Друкувати та записати',
            QtWidgets.QMessageBox.ActionRole)
        buttonY = kassir_question.button(
            QtWidgets.QMessageBox.Yes)
        buttonY.setText('Записати')
        buttonN = kassir_question.button(
            QtWidgets.QMessageBox.No)
        buttonN.setText('Відміна')
        kassir_question.exec_()
        if kassir_question.clickedButton(
        ) == buttonY:
            print('Yes clicked.')
            self.update_entrance_record_by_kassir()
            car_list.remove(self.record.avto)
            # clear fields
            self.postachalnik.clear()
            self.car_num.clear()
            self.zasor.clear()
        if kassir_question.clickedButton(
        ) == buttonN:
            print('No clicked.')
        if kassir_question.clickedButton(
        ) == printButton:
            print('Print clicked.')
            self.update_entrance_record_by_kassir()
            filename = tempfile.mktemp(".txt")
            open(filename, "w").write(printstring)
            print(printstring)

            query = "UPDATE records SET tara = %d, is_enter = %d, is_oplacheno = %d ,is_finished =%d, exit_time=now() WHERE car_num = '%s'" % (
                self.record.vaga,
                self.record.is_enter,
                self.record.is_oplacheno,
                self.record.if_finished,
                self.record.avto)
            write_to_db(query)
            # win32api.ShellExecute(
            #     0, "printto", filename, '"%s"' %
            #     win32print.GetDefaultPrinter(),
            #     ".", 0)
            car_list.remove(self.record.avto)
            self.postachalnik.clear()
            self.car_num.clear()
            # self.material_table.setRowCount(0)
            self.zasor.clear()

    def append_postachalnik(self):
        self.record.postachalnik = self.postachalnik.text()
        result = make_request("SELECT name FROM postachalniky WHERE name='%s'"
                              % self.record.postachalnik)
        print(result)
        if len(result) == 0 and self.record.postachalnik != "":
            write_to_db(
                "INSERT INTO postachalniky(name,car_num) VALUES('%s','%s')" %
                (self.record.postachalnik, self.record.avto))
            postachalnik_list.append(self.record.postachalnik)
            self.postachalnik_completer = QtWidgets.QCompleter(
                postachalnik_list)
            self.postachalnik_completer.setCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
            self.postachalnik.setCompleter(self.postachalnik_completer)

    def append_material(self):
        result = make_request(
            "SELECT material FROM materials WHERE material='%s'" %
            self.record.material)
        print(result)
        if len(result) == 0 and self.record.material != "":
            write_to_db("INSERT INTO materials(material) VALUES('%s')" %
                        self.record.material)
            materials.append(self.record.material)
            self.material_completer = QtWidgets.QCompleter(materials)
            self.material_completer.setCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
            self.material.setCompleter(self.material_completer)

    def check_exit_weight(self, old_weight, current_weight):
        result = make_request(
            "SELECT * FROM records WHERE car_num ='%s' AND is_finished = 0"
            % self.record.avto)
        print(result)
        if (len(result) == 0):
            if (self.rashod_checkbox.isChecked()):
                QtWidgets.QMessageBox.about(
                    self, 'Направте авто на завантаження',
                    'Направте на завантаження')
            else:
                QtWidgets.QMessageBox.about(
                    self, 'Направте авто на розвантаження',
                    'Направте на розвантаження')
            return False
        weight_before = result[0][2]
        self.record.brutto = weight_before
        self.record.tara = self.record.vaga
        print(weight_before, self.record.vaga)
        print("Rashod is checked",self.rashod_checkbox.isChecked())
        if self.rashod_checkbox.isChecked():
            return weight_before <= self.record.vaga
        return weight_before >= self.record.vaga

    def check_record_weight(self, old_weight, current_weight):
        print("record weight_before = ", old_weight)
        vaga = 0
        total_json_values_sum = self.get_total_json_values(self.materials_json_value)
        if self.rashod_checkbox.isChecked():
            vaga = self.record.vaga - old_weight
        else:
            vaga = old_weight - self.record.vaga
        self.record.netto = vaga
        return total_json_values_sum > self.record.netto


    def auto_entrance(self):
        self.record.is_enter = 1
        print("В'їзд")
        self.record.is_oplacheno = 0
        # check if car unloaded
        result = make_request(
            "SELECT * FROM records WHERE car_num ='%s' AND is_finished = 0"
            % self.record.avto)
        print(result)
        if (len(result) > 0):
            QtWidgets.QMessageBox.about(self, 'Авто на розвантаженні',
                                        'Авто на розвантаженні')
            return False

        car_list.append(self.record.avto)
        self.pending_car_list.clear()
        self.pending_car_list.addItems(car_list)
        print(self.record.material)
        is_rashod = 0
        if (self.rashod_checkbox.isChecked()):
            is_rashod = 1
        query = "INSERT INTO records (car_num, brutto,kassir,postachalnik,material,price,is_enter,is_oplacheno,is_finished,zasor,is_rashod) VALUES('%s',%d,'%s','%s','%s',%f,%d,%d,%d,%d,%d)" % (
            self.record.avto, self.record.vaga, self.record.kassir,
            self.record.postachalnik, self.record.material,
            self.record.price, self.record.is_enter,
            self.record.is_oplacheno, self.record.if_finished,
            self.record.zasor, is_rashod)
        write_to_db(query)
        # self.material_table.setRowCount(0)
        self.record.clear_values()
        return True

    def auto_exit(self):
        self.record.is_enter = 0
        # if self.pay_checkbox.isChecked():
        #     self.record.is_oplacheno = 1
        print('Выезд')
        self.record.if_finished = 1
        result = make_request(
            "SELECT * FROM records WHERE car_num ='%s' AND is_finished = 0"
            % self.record.avto)
        print(result)
        if (len(result) == 0):
            QtWidgets.QMessageBox.about(
                self, 'Направте авто на розвантаження',
                'Направте на розвантаження')
            return False

        weight_before = result[0][2]
        self.record.brutto = weight_before
        self.record.tara = self.record.vaga
        enter_time = result[0][0]
        print(weight_before, self.record.vaga)
        if self.check_exit_weight(weight_before,self.record.vaga):
            # self.pending_car_list.addItem(self.record.avto)
            for i in car_list:
                if i == self.record.avto:
                    print(i, self.record.avto)
                    try:
                        result = make_request("SELECT now()")
                        exit_time = result[0][0]
                        diff_time = exit_time - enter_time
                        print(diff_time)
                        print("weight_before = ", weight_before)
                        vaga = weight_before - self.record.vaga
                        self.record.netto = vaga
                        # total_json_values_sum = self.get_total_json_values(self.materials_json_value)
                        # if self.check_record_weight(total_json_values_sum, self.record.netto):
                        #     QtWidgets.QMessageBox.about(
                        #         self,
                        #         'Вага у таблиці більше веса нетто',
                        #         'Вага (%d) у таблиці \n\rбільше ваги нетто (%d)'
                        #         % (total_json_values_sum,
                        #            self.record.netto))
                        #     # return
                        # data = '{0:%d-%m-%Y %H:%M:%S}'.format(
                        #     datetime.datetime.now())
                        # diff_time_str = str(diff_time)
                        self.confirm_window(weight_before)

                        self.pending_car_list.clear()
                        self.pending_car_list.addItems(car_list)
                        self.record.clear_values()
                        return True
                    except Exception as e:
                        print(e)
                        QtWidgets.QMessageBox.about(
                            self, 'Авто не було на розвантаженні',
                            'Направте на розвантаження')
                        return False
        else:
            QtWidgets.QMessageBox.about(
                self, 'Проблема з вагою авто',
                'Вага до розвантаження більше ніж після')
            return False

    def get_total_json_values(self, material_json):
        total_json_values_sum = 0
        for key in material_json.keys():
            total_json_values_sum = total_json_values_sum + int(
                material_json[key]['weight'])
        print("Total json sum is ", total_json_values_sum)
        return total_json_values_sum

    def write_data(self):
        self.record.clear_values()
        self.record.avto = self.car_num.text()
        # get values from table
        self.materials_json_value = {}
        dumps = json.dumps(self.materials_json_value, sort_keys=True, indent=4)
        print(json.loads(dumps))
        # check if postachalnik in list
        if self.postachalnik.text() == "":
            return

        self.append_postachalnik()
        self.append_material()

        if self.price.text() != '':
            self.record.price = float(self.price.text().replace(',', '.'))
            print('price is:', self.record.price)
        self.record.kassir = self.kassir.currentText()
        self.record.vaga = self.weight.intValue()
        if self.zasor.text() == '':
            self.record.zasor = 0
            self.zasor.setText("0")
        else:
            self.record.zasor = int(self.zasor.text())
        self.record.print_values()
        self.record.material = json.dumps(
            self.materials_json_value, ensure_ascii=False)
        if self.record.is_ok():
            if self.entrance_checkbox.isChecked():
                self.auto_entrance()
            else:
                self.auto_exit()
        else:
            print("Ups something wrong")
            QtWidgets.QMessageBox.about(self, 'Отримайте вагу', 'Отримайте вагу')
            self.record.print_values()
        # self.reload_archive()
        comm.reload_all.emit()
        mqtt_client.publish("/reload", "1")

    def fillData(self, index):
        # print(self.pending_car_list.itemText(index))
        num = self.pending_car_list.currentItem().text()
        print(num)
        result = make_request(
            "SELECT * FROM records WHERE car_num ='%s' AND is_finished = 0" %
            num)
        print(result)
        if (len(result) > 0):
            try:
                self.car_num.setText(result[0][1])
                combo_index = self.kassir.findText(result[0][4],
                                                   QtCore.Qt.MatchFixedString)
                if combo_index >= 0:
                    self.kassir.setCurrentIndex(combo_index)
                # self.material.setText(result[0][6])
                # self.material_table.setRowCount(0)
                self.price.setText(str(result[0][7]))
                self.postachalnik.setText(result[0][5])
                self.zasor.setText(str(result[0][13]))
                if result[0][16] == 1:
                    self.rashod_checkbox.setChecked(True)
                material_json_dumps = json.loads(result[0][6].replace(
                    '\"', '"'))
                print(material_json_dumps)
                print(type(material_json_dumps))
                # for key in material_json_dumps.keys():
                #     print(key)
                #     rowPosition = self.material_table.rowCount()
                #     self.material_table.insertRow(rowPosition)
                #     self.material_table.setItem(
                #         rowPosition, 0, QtWidgets.QTableWidgetItem(key))
                #     self.material_table.setItem(
                #         rowPosition, 1,
                #         QtWidgets.QTableWidgetItem(
                #             str(material_json_dumps[key]['weight'])))
                # str(self.weight.intValue())))
            except Exception as e:
                print(e)
                print('Error')

    def onActivated(self, index):
        kassa = self.kassir.itemText(index)
        self.record.kassir = kassa
        self.record.print_values()
        # self.active_kassir = self.kassir.itemText(index)

    def onMaterialActivated(self, index):
        mat = self.material.itemText(index)
        self.record.material = mat
        self.record.print_values()
        # print(mat)

    def setEntrance(self, state):
        if state == QtCore.Qt.Checked:
            self.record.is_enter = 1
            print("В'їзд")
        else:
            self.record.is_enter = 1
            print('Виїзд')

    def setPayment(self, state):
        if state == QtCore.Qt.Checked:
            self.record.is_oplacheno = 1
            print('Сплачено')
        else:
            self.record.is_oplacheno = 0
            print('Оплата відсутня')


app = QtWidgets.QApplication(sys.argv)
# a_window = Window()
a_window = MainWindow()
a_window.show()
sys.exit(app.exec_())
