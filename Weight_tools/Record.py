import csv
import datetime
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from Weight_tools.tools import *
from Weight_tools.Checkable_combo import CheckableComboBox
# from weights import mqtt_client


class Record:
    comm = None
    def __init__(self):
        self.kassir = ""
        self.avto = ""
        self.postachalnik = ""
        self.vaga = 0
        self.material = ""
        self.price = 0
        self.is_enter = 0
        self.is_oplacheno = 0
        self.if_finished = 0
        self.brutto = 0
        self.tara = 0
        self.netto = 0
        self.zasor = 0

    def print_values(self):
        print("Kassir: " + self.kassir + " Avto: " + self.avto + " Vaga: " + str(
            self.vaga) + " kg Material: " + self.material + " Price: " + str(self.price))

    def clear_values(self):
        self.kassir = ""
        self.avto = ""
        self.postachalnik = ""
        self.vaga = 0
        self.material = ""
        self.price = 0
        self.is_enter = 0
        self.is_oplacheno = 0
        self.if_finished = 0
        self.brutto = 0
        self.tara = 0
        self.netto = 0
        self.zasor = 0

    def is_ok(self):
        if self.kassir == "" or self.avto == "" or self.postachalnik == "" or self.vaga == 0 or self.material == "":  # or self.price == 0 :
            return False
        return True

class DisplayRecords(QtWidgets.QMainWindow):
    def __init__(self,
                 parent=None,
                 result=None,
                 date=None,
                 end_date=None,
                 bn=0):
        super().__init__(parent)
        self.date = date
        self.end_date = end_date
        self.result = result
        self.bn = bn
        self.init_ui()

    def init_ui(self):
        self.sum_material_dict = {}
        self.postach_list = set()
        self.setMinimumSize(QtCore.QSize(1300, 180))
        if self.date and self.end_date:
            self.setWindowTitle("Звіт за період з %s по %s" %
                                ('{0:%d-%m-%Y}'.format(self.end_date),
                                 '{0:%d-%m-%Y}'.format(self.date)))
        elif self.date:
            self.setWindowTitle(
                "Звіт за %s" % '{0:%d-%m-%Y}'.format(self.date))
        else:
            self.setWindowTitle("Постачальник %s" % self.result[0][5])
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        print(self.result)
        records_num = len(self.result)
        print("Кількість записів", records_num)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QtWidgets.QGridLayout()
        self.central_widget.setLayout(self.grid_layout)
        self.table = QtWidgets.QTableWidget(self)
        self.header = [
            "№ док", "Дата", "Постачальник", "Номер авто", "Матеріал",
            "Вага в кг", "Вага нетто заг.", "Ціна за кг", "Засміч.",
            "До сплати", "Час розвантаження", "Касир"
        ]
        self.table.setColumnCount(len(self.header))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.header)
        for i in range(len(self.header)):
            self.table.horizontalHeaderItem(i).setToolTip(self.header[i])
            self.table.horizontalHeaderItem(i).setTextAlignment(
                QtCore.Qt.AlignLeft)
        counter = 0
        total_summ = 0
        row_index = 0
        if (len(self.result) == 0):
            self.table.resizeColumnsToContents()
            self.grid_layout.addWidget(self.table, 0, 0)
            return
        for i in self.result:
            print(i)
            print("Json result ", self.result[counter][6])
            ########
            old_type_zasor= self.result[counter][13]
            zasor_flag = 1
            ########
            records_materials = json.loads(self.result[counter][6])
            if self.bn==1:
                for element in polymer:
                    records_materials.pop(element, None)
            if self.bn == 2:
                for element in makulatura:
                    records_materials.pop(element, None)
            if self.bn == 3:
                multi = polymer + makulatura
                keys_to_delete = []
                for key in records_materials.keys():
                    if "-бн" not in key:
                    # if key not in multi:
                        keys_to_delete.append(key)
                for kd in keys_to_delete:
                    records_materials.pop(kd, None)
            if self.bn == 4:
                multi = polymer + makulatura
                keys_to_delete = []
                for key in records_materials.keys():
                    if key  in multi:
                        keys_to_delete.append(key)
                for kd in keys_to_delete:
                    records_materials.pop(kd, None)
            for key in records_materials.keys():
                print(key, records_materials[key])
                self.table.insertRow(row_index)
                print(self.result[counter][2] - self.result[counter][3])
                record_weight = round(
                    self.result[counter][7] *
                    (self.result[counter][2] - self.result[counter][3]),
                    3) - self.result[counter][13]
                self.table.setItem(row_index, 0,
                                   QtWidgets.QTableWidgetItem(
                                       str(self.result[counter][14])))
                self.table.setItem(row_index, 1,
                                   QtWidgets.QTableWidgetItem(
                                       '{0:%d-%m-%Y %H:%M:%S}'.format(
                                           self.result[counter][0])))
                self.table.setItem(row_index, 2,
                                   QtWidgets.QTableWidgetItem(
                                       self.result[counter][5]))
                self.table.setItem(row_index, 3,
                                   QtWidgets.QTableWidgetItem(
                                       self.result[counter][1]))
                self.table.setItem(row_index, 4,
                                   QtWidgets.QTableWidgetItem(key))
                self.postach_list.add(self.result[counter][5])
                if key in self.sum_material_dict:
                    self.sum_material_dict[key][
                        'total_cost'] = self.sum_material_dict[key]['total_cost'] + float(
                            records_materials[key]['weight'] *
                            records_materials[key]['price'])
                    self.sum_material_dict[key][
                        'weight'] = self.sum_material_dict[key]['weight'] + records_materials[key]['weight']
                else:
                    self.sum_material_dict[key] = {
                        'total_cost':
                        float(records_materials[key]['weight'] *
                              records_materials[key]['price']),
                        'weight':
                        records_materials[key]['weight']
                    }
                self.table.setItem(row_index, 5,
                                   QtWidgets.QTableWidgetItem(
                                       str(records_materials[key]['weight'])))
                self.table.setItem(
                    row_index, 6,
                    QtWidgets.QTableWidgetItem(
                        str(self.result[counter][2] - self.result[counter][3])
                    ))
                self.table.setItem(
                    row_index, 7,
                    QtWidgets.QTableWidgetItem(
                        str(records_materials[key][
                            'price'])))  #self.result[counter][7])))
                if "trash" in records_materials[key].keys():
                    self.table.setItem(row_index, 8,
                                   QtWidgets.QTableWidgetItem(
                                       str(records_materials[key]['trash'])))
                elif old_type_zasor !=0 and zasor_flag:
                    self.table.setItem(row_index, 8,
                                   QtWidgets.QTableWidgetItem(
                                       str(old_type_zasor)))
                    zasor_flag = 0
                else:
                    self.table.setItem(row_index, 8,
                                   QtWidgets.QTableWidgetItem(
                                       str(0)))
                total_summ = total_summ + (records_materials[key]['weight'] *
                                           records_materials[key]['price'])
                print(total_summ)
                self.table.setItem(
                    row_index, 9,
                    QtWidgets.QTableWidgetItem("{0:.2f}".format(
                        records_materials[key]['weight'] * records_materials[
                            key]['price'])))  #str(record_weight)))
                enter_time = self.result[counter][0]
                exit_time = self.result[counter][11]
                if (exit_time != None):
                    diff_time = exit_time - enter_time
                    print(diff_time)
                    data = '{0:%Y-%m-%d %H:%M:%S}'.format(
                        datetime.datetime.now())
                    diff_time_str = str(diff_time)
                    self.table.setItem(
                        row_index, 10,
                        QtWidgets.QTableWidgetItem(diff_time_str))
                else:
                    diff_time_str = "0:15:00"
                    self.table.setItem(
                        row_index, 10,
                        QtWidgets.QTableWidgetItem(diff_time_str))
                self.table.setItem(row_index, 11,
                                   QtWidgets.QTableWidgetItem(
                                       self.result[counter][4]))
                row_index = row_index + 1
            counter = counter + 1
        self.table.resizeColumnsToContents()
        print(self.postach_list)
        self.result = self.result
        self.print_button = QtWidgets.QPushButton("Друк")
        self.show_record = QtWidgets.QPushButton("Дивитися запис")
        self.csv_button = QtWidgets.QPushButton("Завантажити у файл")
        # self.info_label = QtWidgets.QLabel('Усього: ' + str(total_summ))
        info_summary = 'Усього: ' + "{0:.2f}".format(total_summ) + "\n"
        print(self.sum_material_dict)
        for key, value in self.sum_material_dict.items():
            if len(key) >= 7:
                info_summary = info_summary + key + ": \t" + str(
                    value['weight']) + 'кг\t' + str("{0:.2f}".format(
                        value['total_cost'], 3)) + " грн \n"
            else:
                info_summary = info_summary + key + ": \t\t" + str(
                    value['weight']) + 'кг\t' + str("{0:.2f}".format(
                        value['total_cost'], 3)) + " грн \n"
        self.info_box = QtWidgets.QHBoxLayout()
        self.short_info_box = QtWidgets.QVBoxLayout()
        self.filter_box = QtWidgets.QVBoxLayout()
        self.post_filter = CheckableComboBox()#QtWidgets.QComboBox()
        self.filter_button = QtWidgets.QPushButton("Фільтр постачальника")
        self.mater_filter = CheckableComboBox()
        self.materf_button = QtWidgets.QPushButton("Фільтр матеріалів")
        self.total_cost = QtWidgets.QLabel(
            'Усього: ' + "{0:.2f}".format(total_summ))
        # self.post_filter.setFont(self.newfont)

        # self.post_filter.addItems(sorted(self.postach_list))
        sorted(self.postach_list)
        for p in sorted(self.postach_list):
            self.post_filter.addItem(p)
        self.filter_box.addWidget(self.post_filter)
        self.filter_box.addWidget(self.filter_button)
        self.filter_box.addWidget(self.mater_filter)
        self.filter_box.addWidget(self.materf_button)
        self.filter_box.addWidget(self.total_cost)
        self.filter_box.setAlignment(QtCore.Qt.AlignTop)
        # self.info_label = QtWidgets.QLabel(info_summary)
        # self.info_summary = info_summary
        self.info_label = QtWidgets.QTableWidget(self)
        self.header = [
            "Товар",
            "Вага в кг",
            "Вартість за кг",
            "Сума",
        ]
        self.info_label.setColumnCount(len(self.header))
        self.info_label.setRowCount(0)
        self.info_label.setHorizontalHeaderLabels(self.header)
        self.info_label.setMaximumWidth(800)
        # self.info_label.setAlignment(QtCore.Qt.AlignRight)
        row_index = 0
        for key in self.sum_material_dict:
            self.info_label.insertRow(row_index)
            self.info_label.setItem(row_index, 0,
                                    QtWidgets.QTableWidgetItem(str(key)))
            self.info_label.setItem(
                row_index, 1,
                QtWidgets.QTableWidgetItem(
                    str(self.sum_material_dict[key]['weight'])))
            self.info_label.setItem(
                row_index, 3,
                QtWidgets.QTableWidgetItem(
                    str("{0:.2f}".format(
                        self.sum_material_dict[key]['total_cost'], 3))))
            if self.sum_material_dict[key]['weight'] != 0:
                self.info_label.setItem(
                    row_index, 2,
                    QtWidgets.QTableWidgetItem(
                        str("{0:.2f}".format(
                            self.sum_material_dict[key]['total_cost'] /
                            self.sum_material_dict[key]['weight'], 3))))
            else:
                self.info_label.setItem(row_index, 2,
                                        QtWidgets.QTableWidgetItem(
                                            str("{0:.2f}".format(0, 3))))
            self.info_label.item(row_index,
                                 1).setTextAlignment(QtCore.Qt.AlignRight
                                                     | QtCore.Qt.AlignVCenter)
            self.info_label.item(row_index,
                                 2).setTextAlignment(QtCore.Qt.AlignRight
                                                     | QtCore.Qt.AlignVCenter)
            self.info_label.item(row_index,
                                 3).setTextAlignment(QtCore.Qt.AlignRight
                                                     | QtCore.Qt.AlignVCenter)
            row_index = row_index + 1
        self.short_info_button = QtWidgets.QPushButton(
            "Зберегти короткий звіт")
        self.summ_value = QtWidgets.QLabel()
        for p in sorted(list(self.sum_material_dict.keys())):
            self.mater_filter.addItem(p)
        self.filter_box.addWidget(self.summ_value)
        self.short_info_box.addWidget(self.info_label)
        self.short_info_box.addWidget(self.short_info_button)
        self.info_box.addLayout(self.short_info_box)
        self.info_box.addLayout(self.filter_box)
        self.button_box = QtWidgets.QHBoxLayout()
        self.button_box.addWidget(self.print_button)
        self.button_box.addWidget(self.show_record)
        self.button_box.addWidget(self.csv_button)
        self.grid_layout.addWidget(self.table, 0, 0)
        self.grid_layout.addLayout(self.info_box, 1, 0)
        self.grid_layout.addLayout(self.button_box, 2, 0)
        self.print_button.clicked.connect(self.print_from_current_row)
        self.show_record.clicked.connect(self.show_record_dialog)
        self.csv_button.clicked.connect(self.download_csv)
        self.short_info_button.clicked.connect(self.download_short_csv)
        self.filter_button.clicked.connect(self.show_filtered_data)
        self.materf_button.clicked.connect(self.show_filtered_mater)
        self.table.itemSelectionChanged.connect(self.cell_was_clicked)

    def cell_was_clicked(self):
        total_sum = 0
        for item in self.table.selectedItems():
            print(item.column())
            if item.column() == 9:
                print(item.text())
                total_sum = total_sum + float(item.text())
        # item = self.report_table.itemAt(row, column)
        if total_sum:
            self.summ_value.setText("Сумма обраних комірок: %.2f" % total_sum)
        else:
            self.summ_value.setText("")
    def get_postach_filter(self):
        p_values=[]
        for i in range(self.post_filter.count()):
            if self.post_filter.itemChecked(i):
                p_values.append( self.post_filter.itemText(i))
        print(p_values)
        return p_values

    def get_mater_filter(self):
        p_values=[]
        for i in range(self.mater_filter.count()):
            if self.mater_filter.itemChecked(i):
                p_values.append( self.mater_filter.itemText(i))
        print(p_values)
        return p_values

    def show_filtered_mater(self):
        filtr_postach = self.get_mater_filter()
        # filtr_postach = str(self.post_filter.currentText())
        result = []
        for i in self.result:
            print(i[6])
            json_vals = json.loads(i[6])
            json_keys = json_vals.keys()
            keys_to_delete =[]
            for k in json_keys:
                if k not in(filtr_postach):
                    keys_to_delete.append(k)
            for k in keys_to_delete:
                json_vals.pop(k,None)
            if json_vals:
                vals = list(i)
                vals[6] = json.dumps(json_vals)
                result.append(tuple(vals))

                # if p in json.loads(i[6]).keys():
                    # result.append(i)
        print(filtr_postach, result)
        DisplayRecords(self, result).show()

    def show_filtered_data(self):
        filtr_postach = self.get_postach_filter()
        # filtr_postach = str(self.post_filter.currentText())
        result = []
        for i in self.result:
            for p in filtr_postach:
                if p in i:
                    result.append(i)
        # print(filtr_postach, result)
        DisplayRecords(self, result).show()

    def download_short_csv(self):
        print(self.sum_material_dict)
        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            " CSV (*.csv);;Все файлы (*)",
            options=options)
        if fileName:
            print(fileName)
            with open(fileName, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                row_count = 0
                writer.writerow(['Материал', 'Вес', 'Цена'])
                for key in self.sum_material_dict:
                    row_append = []
                    row_append.append(key)
                    row_append.append(
                        str(self.sum_material_dict[key]['weight']).replace(
                            '.', ','))
                    row_append.append(
                        str(self.sum_material_dict[key]['total_cost']).replace(
                            '.', ','))
                    print(row_append)
                    writer.writerow(row_append)

    def download_csv(self):
        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            " CSV (*.csv);;Все файлы (*)",
            options=options)
        if fileName:
            print(fileName)
            with open(fileName, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                row_count = 0
                writer.writerow([
                    'Номер', 'Дата', 'Поставщик', 'Номер авто', 'Материал',
                    'Вес', 'Вес нетто', 'Цена за кг', 'Засор', 'к оплате',
                    'Время разгрузки', 'Кассир'
                ])
                while row_count != self.table.rowCount():
                    row_append = []
                    column_counter = 0
                    while column_counter != 12:
                        row_append.append(
                            self.table.item(row_count,
                                            column_counter).text().replace(
                                                '.', ','))
                        column_counter += 1
                    print(row_append)
                    writer.writerow(row_append)
                    row_count += 1

    def show_record_dialog(self):
        cur_row = self.table.currentRow()
        print(cur_row)
        if cur_row == -1:
            QtWidgets.QMessageBox.about(self, 'Выберите ряд', 'Выберите ряд')
        else:
            doc_number = int(self.table.item(cur_row, 0).text())
            QtWidgets.QMessageBox.about(self, str(doc_number),
                                        get_check_data(doc_number))

    def print_from_current_row(self):
        cur_row = self.table.currentRow()
        print(cur_row)
        if cur_row == -1:
            QtWidgets.QMessageBox.about(self, 'Выберите ряд', 'Выберите ряд')
        else:
            doc_number = int(self.table.item(cur_row, 0).text())
            print_check(doc_number)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.table.setRowCount(0)
            if self.date and self.end_date:
                self.result = make_request(
                    "SELECT * FROM records WHERE DATE(date) >='%s' and DATE(date)<='%s' AND is_finished = 1 AND is_archived = 1"
                    % ('{0:%Y-%m-%d}'.format(self.end_date),
                       '{0:%Y-%m-%d}'.format(self.date)))
            elif self.date:
                self.result = make_request(
                    "SELECT * FROM records WHERE DATE(date) ='%s' AND is_finished = 1 AND is_archived = 1"
                    % '{0:%Y-%m-%d}'.format(self.date))
            print(self.result)
            records_num = len(self.result)
            self.central_widget.setLayout(self.grid_layout)
            self.table.setColumnCount(len(self.header))
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels(self.header)
            for i in range(len(self.header)):
                self.table.horizontalHeaderItem(i).setToolTip(self.header[i])
                self.table.horizontalHeaderItem(i).setTextAlignment(
                    QtCore.Qt.AlignLeft)
            counter = 0
            total_summ = 0
            row_index = 0
            if (len(self.result) == 0):
                self.table.resizeColumnsToContents()
                self.grid_layout.addWidget(self.table, 0, 0)
                return
            for i in self.result:
                print(i)
                print("Json result ", self.result[counter][6])
                records_materials = json.loads(self.result[counter][6])
                for key in records_materials.keys():
                    print(key, records_materials[key])
                    self.table.insertRow(row_index)
                    print(self.result[counter][2] - self.result[counter][3])
                    record_weight = round(
                        self.result[counter][7] *
                        (self.result[counter][2] - self.result[counter][3]),
                        3) - self.result[counter][13]
                    self.table.setItem(row_index, 0,
                                       QtWidgets.QTableWidgetItem(
                                           str(self.result[counter][14])))
                    self.table.setItem(row_index, 1,
                                       QtWidgets.QTableWidgetItem(
                                           '{0:%Y-%m-%d %H:%M:%S}'.format(
                                               self.result[counter][0])))
                    self.table.setItem(row_index, 2,
                                       QtWidgets.QTableWidgetItem(
                                           self.result[counter][5]))
                    self.table.setItem(row_index, 3,
                                       QtWidgets.QTableWidgetItem(
                                           self.result[counter][1]))
                    self.table.setItem(row_index, 4,
                                       QtWidgets.QTableWidgetItem(key))
                    if key in self.sum_material_dict:
                        self.sum_material_dict[key][
                            'total_cost'] = self.sum_material_dict[key]['total_cost'] + float(
                                records_materials[key]['weight'] *
                                records_materials[key]['price'])
                        self.sum_material_dict[key][
                            'weight'] = self.sum_material_dict[key]['weight'] + records_materials[key]['weight']
                    else:
                        self.sum_material_dict[key] = {
                            'total_cost':
                            float(records_materials[key]['weight'] *
                                  records_materials[key]['price']),
                            'weight':
                            records_materials[key]['weight']
                        }

                    self.table.setItem(
                        row_index, 5,
                        QtWidgets.QTableWidgetItem(
                            str(records_materials[key]['weight'])))
                    self.table.setItem(row_index, 6,
                                       QtWidgets.QTableWidgetItem(
                                           str(self.result[counter][2] -
                                               self.result[counter][3])))
                    self.table.setItem(
                        row_index, 7,
                        QtWidgets.QTableWidgetItem(
                            str(records_materials[key][
                                'price'])))  #self.result[counter][7])))
                    self.table.setItem(row_index, 8,
                                       QtWidgets.QTableWidgetItem(
                                           str(self.result[counter][13])))
                    total_summ = total_summ + (
                        records_materials[key]['weight'] *
                        records_materials[key]['price'])
                    print(total_summ)
                    self.table.setItem(
                        row_index, 9,
                        QtWidgets.QTableWidgetItem("{0:.2f}".format(
                            records_materials[key]['weight'] *
                            records_materials[key][
                                'price'])))  #str(record_weight)))
                    enter_time = self.result[counter][0]
                    exit_time = self.result[counter][11]
                    if (exit_time != None):
                        diff_time = exit_time - enter_time
                        print(diff_time)
                        data = '{0:%Y-%m-%d %H:%M:%S}'.format(
                            datetime.datetime.now())
                        diff_time_str = str(diff_time)
                        self.table.setItem(
                            row_index, 10,
                            QtWidgets.QTableWidgetItem(diff_time_str))
                    else:
                        diff_time_str = "0:15:00"
                        self.table.setItem(
                            row_index, 10,
                            QtWidgets.QTableWidgetItem(diff_time_str))
                    self.table.setItem(row_index, 11,
                                       QtWidgets.QTableWidgetItem(
                                           self.result[counter][4]))
                    row_index = row_index + 1
                counter = counter + 1
            self.table.resizeColumnsToContents()
            self.info_label = QtWidgets.QLabel(
                'Итого: ' + "{0:.2f}".format(total_summ))
            # print(self.sum_material_dict)
            info_summary = 'Итого: ' + str(total_summ) + "\n"
            for key, value in self.sum_material_dict.items():
                if len(key) >= 7:
                    info_summary = info_summary + key + ": \t" + str(
                        value['weight']) + 'кг\t' + str(
                            "{0:.2f}".format(value['total_cost'],
                                             3)) + " грн \n"
                else:
                    info_summary = info_summary + key + ": \t\t" + str(
                        value['weight']) + 'кг\t' + str(
                            "{0:.2f}".format(value['total_cost'],
                                             3)) + " грн \n"
            self.info_label.setText(info_summary)

class RecordSelector(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RecordSelector, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.id_record_label = QtWidgets.QLabel("Номер документу")
        self.id_record = QtWidgets.QLineEdit()
        self.id_record_box = QtWidgets.QHBoxLayout()
        self.id_record_box.addStretch()
        self.id_record_box.addWidget(self.id_record_label)
        self.id_record_box.addWidget(self.id_record)
        # nice widget for editing the date
        layout.addLayout(self.id_record_box)
        # OK and Cancel buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def record_id(self):
        return self.id_record.text()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getRecordID(parent=None):
        dialog = RecordSelector(parent)
        result = dialog.exec_()
        id_rec = dialog.record_id()
        return (id_rec, result == QtWidgets.QDialog.Accepted)


class ReturnRecord(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Повернення запису")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        self.num_label = QtWidgets.QLabel('Номер запису')
        self.num_label.setFont(self.newfont)
        self.num = QtWidgets.QLineEdit()
        self.num.setFont(self.newfont)
        self.write_button = QtWidgets.QPushButton('Повернути')
        self.write_button.setFont(self.newfont)
        num_box = QtWidgets.QHBoxLayout()
        num_box.addStretch()
        num_box.addWidget(self.num_label)
        num_box.addWidget(self.num)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(num_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.write)
        central_widget.setLayout(vbox)

    def write(self):
        try:
            num = int(self.num.text())
            print(num)
            if num:
                write_to_db(
                    "UPDATE `records` SET is_archived=0 WHERE id=%d" % num)
                # mqtt_client.publish("/reload", "1")
        except Exception as e:
            raise e
        # if postach != "":
        #     write_to_db(
        #         "INSERT INTO postachalniky(name,phone,contact,car_num) VALUES('%s','%s','%s','%s')"
        #         % (postach, phone, contact, car_num))
        #     print(" Додати")


class AddRecord(QtWidgets.QMainWindow):
    def __init__(self, parent=None, id_rec=None):
        super().__init__(parent)
        # self.id_rec = id_rec
        self.init_ui()

    def init_ui(self):
        respond = make_request("SELECT dozvol from `dozvol` WHERE id=1")
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Додавання запису")
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)

        self.label_vbox = QtWidgets.QVBoxLayout(self)
        self.data_label = QtWidgets.QLabel("Дата")
        self.brutto_label = QtWidgets.QLabel("Брутто")
        self.tara_label = QtWidgets.QLabel("Тара")
        self.postach_label = QtWidgets.QLabel("Постачальник")
        self.carnum_label = QtWidgets.QLabel("Номер Авто")

        self.data_label.setFont(self.newfont)
        self.brutto_label.setFont(self.newfont)
        self.tara_label.setFont(self.newfont)
        self.postach_label.setFont(self.newfont)
        self.carnum_label.setFont(self.newfont)

        self.label_vbox.addWidget(self.data_label)
        self.label_vbox.addWidget(self.brutto_label)
        self.label_vbox.addWidget(self.tara_label)
        self.label_vbox.addWidget(self.postach_label)
        self.label_vbox.addWidget(self.carnum_label)

        self.edit_vbox = QtWidgets.QVBoxLayout(self)

        self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QtCore.QDateTime.currentDateTime())

        self.brutto = QtWidgets.QLineEdit()
        self.tara = QtWidgets.QLineEdit()
        self.postach = QtWidgets.QLineEdit()
        self.carnum = QtWidgets.QLineEdit()
        self.datetime.setFont(self.newfont)
        self.brutto.setFont(self.newfont)
        self.tara.setFont(self.newfont)
        self.postach.setFont(self.newfont)
        self.carnum.setFont(self.newfont)

        self.postachalnik_completer = QtWidgets.QCompleter(postachalnik_list)
        self.postachalnik_completer.setCaseSensitivity(
            QtCore.Qt.CaseInsensitive)
        self.postach.setCompleter(self.postachalnik_completer)

        self.edit_vbox.addWidget(self.datetime)
        self.edit_vbox.addWidget(self.brutto)
        self.edit_vbox.addWidget(self.tara)
        self.edit_vbox.addWidget(self.postach)
        self.edit_vbox.addWidget(self.carnum)

        self.is_rashod = QtWidgets.QCheckBox("Продаж")
        self.is_rashod.setFont(self.newfont)
        self.hbox = QtWidgets.QHBoxLayout(self)
        if (respond[0][0] == 0):
            QtWidgets.QMessageBox.about(self, "Заборонено", "Заборонено")
        else:
            self.hbox.addLayout(self.label_vbox)
            self.hbox.addLayout(self.edit_vbox)

        self.button_box = QtWidgets.QHBoxLayout(self)
        self.add_button = QtWidgets.QPushButton('Записати')
        self.add_button.setFont(self.newfont)
        self.add_button.clicked.connect(self.writeData)

        self.cancel_button = QtWidgets.QPushButton('Відміна')
        self.cancel_button.setFont(self.newfont)
        self.cancel_button.clicked.connect(self.cancel)
        self.button_box.addWidget(self.add_button)
        self.button_box.addWidget(self.cancel_button)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.is_rashod)
        self.vbox.addLayout(self.button_box)
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(self.vbox)
        self.setCentralWidget(central_widget)

    def writeData(self):
        try:
            if self.is_rashod.isChecked():
                tara = int(self.brutto.text())
                brutto = int(self.tara.text())
            else:
                brutto = int(self.brutto.text())
                tara = int(self.tara.text())
        except Exception as e:
            QtWidgets.QMessageBox.about(self, "ERROR", str(e))
            return
        if tara > brutto:
            QtWidgets.QMessageBox.about(self, "Перевірте дані",
                                        "Тара більше Брутто")
            return
        postach = self.postach.text()
        carnum = self.carnum.text()
        date = self.datetime.dateTime().toPyDateTime()
        is_rashod = 0
        if self.is_rashod.isChecked():
            is_rashod = 1
        if brutto and tara and postach and carnum and date:
            request = "INSERT INTO records (date,car_num, brutto, tara, kassir, postachalnik, material,price,is_enter,is_oplacheno,is_finished, exit_time,netto,zasor,is_archived, is_rashod) values('%s','%s',%d,%d,'%s','%s','%s',%f,%d,%d,%d,'%s',%d,%d,%d, %d)" % (
                str(date), carnum, brutto, tara, "Ручне Додавання", postach,
                "{}", 0, 0, 0, 1, str(date), (brutto - tara), 0, 0,is_rashod)
            cur_id = write_to_db(request)
            # mqtt_client.publish("/reload", "1")
            QtWidgets.QMessageBox.about(self, 'Створений запис',
                                        'Створено запис № %d' % cur_id)
            self.brutto.setText("")
            self.tara.setText("")
            self.postach.setText("")
            self.carnum.setText("")
        else:
            QtWidgets.QMessageBox.about(self, 'Перевірте дані',
                                        'Перевірте дані ')
        Record.comm.reload_all.emit()


    def cancel(self):
        self.close()


class RecordEditor(QtWidgets.QMainWindow):
    def __init__(self, parent=None, id_rec=None):
        super().__init__(parent)
        self.id_rec = id_rec
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Редагування запису")
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        result = make_request(
            "SELECT * FROM records WHERE id =%s " % self.id_rec[0])
        print(result)
        print("Json result ", result[0][6])
        records_materials = json.loads(result[0][6])
        self.material_dict = {}
        self.netto_weight = int(result[0][12])
        vbox = QtWidgets.QVBoxLayout()
        self.id_record_label = QtWidgets.QLabel("Номер документу")
        self.id_record = QtWidgets.QLabel(self.id_rec[0])
        self.id_record_label.setFont(self.newfont)
        self.id_record.setFont(self.newfont)
        self.weight_label = QtWidgets.QLabel(
            "Загальна вага по базі = " + str(self.netto_weight))
        id_box = QtWidgets.QHBoxLayout()
        id_box.addStretch()
        id_box.addWidget(self.id_record_label)
        id_box.addWidget(self.id_record)
        vbox.addLayout(id_box)
        self.enter_weight = 0
        for key in records_materials.keys():
            self.material_dict[key] = ({
                0:
                QtWidgets.QLabel(key),
                1:
                QtWidgets.QLabel(
                    str(records_materials[key]['weight']) + " кг"),
                2:
                QtWidgets.QLabel(str(records_materials[key]['price']) + "грн"),
                3:
                QtWidgets.QLabel(
                    str((records_materials[key]['weight'] *
                         records_materials[key]['price'])) + "грн"),
                4:
                QtWidgets.QHBoxLayout(self)
            })
            print(records_materials[key]['weight'])
            # self.material_dict[key][1].setText(str(records_materials[key]['weight']))
            self.material_dict[key][4].addWidget(self.material_dict[key][0])
            self.material_dict[key][4].addWidget(self.material_dict[key][1])
            self.material_dict[key][4].addWidget(self.material_dict[key][2])
            self.material_dict[key][4].addWidget(self.material_dict[key][3])
            # # self.material_dict[key][1].returnPressed.connect(self.weightEnterClicked)
            # self.material_dict[key][1].returnPressed.connect(
            #     lambda: self.weightEnterClicked())
            vbox.addLayout(self.material_dict[key][4])
            self.enter_weight = self.enter_weight + records_materials[key]['weight']
        # print(material_dict)
        self.enter_weight_label = QtWidgets.QLabel(
            "Загальна вага перебірки = " + str(self.enter_weight))
        self.write_button = QtWidgets.QPushButton('Записати зміни')
        self.print_button = QtWidgets.QPushButton('Друк')
        vbox.addWidget(self.weight_label)
        vbox.addWidget(self.enter_weight_label)
        # vbox.addWidget(self.write_button)
        vbox.addWidget(self.print_button)
        # self.write_button.clicked.connect(self.writeData)
        self.print_button.clicked.connect(self.print_doc)
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(vbox)

    def weightEnterClicked(self):
        # print(self.enter_weight)
        self.enter_weight = 0
        for key in self.material_dict.keys():
            self.enter_weight = self.enter_weight + int(
                self.material_dict[key][1].text())
        self.enter_weight_label.setText(
            "Загальна вага = " + str(self.enter_weight))

    def writeData(self):
        pass

    def print_doc(self):
        print_check(self.id_rec[0])

class RemoveRecord(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Повернення запису")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        self.num_label = QtWidgets.QLabel('Номер запису')
        self.num_label.setFont(self.newfont)
        self.num = QtWidgets.QLineEdit()
        self.num.setFont(self.newfont)
        self.write_button = QtWidgets.QPushButton('Видалити')
        self.write_button.setFont(self.newfont)
        num_box = QtWidgets.QHBoxLayout()
        num_box.addStretch()
        num_box.addWidget(self.num_label)
        num_box.addWidget(self.num)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(num_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.write)
        central_widget.setLayout(vbox)

    def write(self):
        try:
            num = int(self.num.text())
            print(num)
            if num:
                write_to_db(
                    "DELETE FROM `records` WHERE id=%d" % num)
                # mqtt_client.publish("/reload", "1")
                self.num.setText("")
                Record.comm.reload_all.emit()
        except Exception as e:
            raise e