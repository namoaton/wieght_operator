from PyQt5 import QtWidgets, QtCore, QtGui
from Weight_tools.tools import *
import json


class EditWaitForArchive(QtWidgets.QMainWindow):
    procDone = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, index=None, result=None,
                 postach_edit=None):
        super().__init__(parent)
        self.index = index
        self.result = result
        self.postach_edit = postach_edit
        # self.postach_edit = 1
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 640))
        self.setWindowTitle("Перевірка запису")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 14, QtGui.QFont.Bold)
        # result = make_request(
        #     "SELECT * FROM records WHERE id =%s" % self.index)
        print(self.result)
        self.id_label = QtWidgets.QLabel("Номер запису у журналі")
        self.id_label.setFont(self.newfont)
        print("Номер запису у журналі", self.index)
        self.id_value = QtWidgets.QLabel(str(self.index))
        self.id_value.setFont(self.newfont)
        self.data_label = QtWidgets.QLabel("Дата запису")
        self.data_label.setFont(self.newfont)
        self.data_value = QtWidgets.QLabel('{0:%d-%m-%Y %H:%M:%S}'.format(
            self.result[0][0]))
        self.data_value.setFont(self.newfont)
        self.car_num_label = QtWidgets.QLabel('Номер авто')
        self.car_num_label.setFont(self.newfont)
        self.car_num = QtWidgets.QLabel(self.result[0][1])
        self.car_num.setFont(self.newfont)
        self.postach_name_label = QtWidgets.QLabel('Постачальник')
        self.postach_name_label.setFont(self.newfont)
        if self.postach_edit:
            self.postach_name = QtWidgets.QComboBox()
            postachalnik_list.sort()
            self.postach_name.addItems(sorted(postachalnik_list))
        else:
            self.postach_name = QtWidgets.QLabel(self.result[0][5])
        self.postach_name.setFont(self.newfont)
        self.netto_label = QtWidgets.QLabel("Вага нетто")
        self.netto_label.setFont(self.newfont)
        # self.netto = self.result[0][12]
        self.netto = int(self.result[0][2]) - int(self.result[0][3])
        self.netto_value = QtWidgets.QLabel(str(self.netto) + " кг")
        self.netto_value.setFont(self.newfont)
        self.brutto_value =  QtWidgets.QLabel(str(self.result[0][2]))
        self.brutto_label = QtWidgets.QLabel('Брутто')
        self.brutto_value.setFont(self.newfont)
        self.brutto_label.setFont(self.newfont)
        self.tara_value =  QtWidgets.QLabel(str(self.result[0][3]))
        self.tara_label = QtWidgets.QLabel('Тара')
        self.tara_value.setFont(self.newfont)
        self.tara_label.setFont(self.newfont)
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.setHorizontalHeaderLabels(
            ["Матеріал", "Вага", "Ціна за кг", "Сума","Засмічення"])
        self.table.horizontalHeaderItem(0).setToolTip("Матеріал ")
        self.table.horizontalHeaderItem(1).setToolTip("Вага ")
        self.table.horizontalHeaderItem(2).setToolTip("Ціна за кг ")
        self.table.horizontalHeaderItem(3).setToolTip("Сума ")
        self.table.horizontalHeaderItem(4).setToolTip("Засмічення ")
        self.table.horizontalHeaderItem(0).setTextAlignment(
            QtCore.Qt.AlignHCenter)
        self.table.horizontalHeaderItem(1).setTextAlignment(
            QtCore.Qt.AlignHCenter)
        self.table.horizontalHeaderItem(2).setTextAlignment(
            QtCore.Qt.AlignHCenter)
        self.table.horizontalHeaderItem(3).setTextAlignment(
            QtCore.Qt.AlignHCenter)
        self.table.horizontalHeaderItem(4).setTextAlignment(
            QtCore.Qt.AlignHCenter)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.header = self.table.horizontalHeader()
        self.header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.header.setStretchLastSection(True)
        #fill table
        materials_json = json.loads(self.result[0][6])
        counter = 0
        row_index = 0
        self.total_summ = 0
        for key in materials_json.keys():
            print(key, materials_json[key])
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(key))
            self.table.setItem(row_index, 1,
                               QtWidgets.QTableWidgetItem(
                                   str(materials_json[key]['weight'])))
            self.table.setItem(row_index, 2,
                               QtWidgets.QTableWidgetItem(
                                   str(materials_json[key]['price'])))
            self.table.setItem(row_index, 3,
                               QtWidgets.QTableWidgetItem(
                                   str(materials_json[key]['weight'] * float(
                                       materials_json[key]['price']))))
            if 'trash' in materials_json[key].keys():
                self.table.setItem(row_index, 4,
                               QtWidgets.QTableWidgetItem(
                                   str(materials_json[key]['trash'])))
                self.total_summ = self.total_summ + materials_json[key]['weight'] + materials_json[key]['trash']
            else:
                self.table.setItem(row_index, 4,
                               QtWidgets.QTableWidgetItem(str(0)))
                self.total_summ = self.total_summ + materials_json[key]['weight']
            row_index = row_index + 1
        print("Total summ", self.total_summ)
        print("Netto ", self.netto)
        self.diff = self.netto - self.total_summ
        print("Diff ", self.diff)
        self.total_summ_label = QtWidgets.QLabel('Перебірка ')
        self.total_summ_label.setFont(self.newfont)
        self.total_summ_value = QtWidgets.QLabel(str(self.total_summ) + " кг")
        self.total_summ_value.setFont(self.newfont)
        self.diff_label = QtWidgets.QLabel('Різниця')
        self.diff_label.setFont(self.newfont)
        self.diff_value = QtWidgets.QLabel(str(self.diff) + " кг")
        self.diff_value.setFont(self.newfont)
        self.zasor_label = QtWidgets.QLabel('Засмічення')
        self.zasor_label.setFont(self.newfont)
        self.zasor_value = QtWidgets.QLineEdit()
        self.zasor_value.setFont(self.newfont)
        self.zasor_value.setText("0")
        self.zasor = 0
        try:
            result = make_request(
                "SELECT zasor FROM records WHERE id =%s" % self.index)
        except:
            result = [[0]]
        self.zasor = result[0][0]
        self.zasor_value.setText(str(self.zasor))
        # print(result[0][0])
        self.write_button = QtWidgets.QPushButton('В архів')
        self.write_button.setFont(self.newfont)
        self.split_button = QtWidgets.QPushButton('Розділити')
        self.split_button.setFont(self.newfont)
        self.print_button = QtWidgets.QPushButton('Друкувати')
        self.print_button.setFont(self.newfont)
        self.cancel_button = QtWidgets.QPushButton('Відміна')
        self.cancel_button.setFont(self.newfont)
        self.addRow_button = QtWidgets.QPushButton("Додати ряд")
        # self.addRow_button.setFont(self.newfont)
        self.mat_input = QtWidgets.QLineEdit()
        self.mat_input_completer = QtWidgets.QCompleter(materials)
        self.mat_input_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.mat_input.setCompleter(self.mat_input_completer)
        self.weigth_input = QtWidgets.QLineEdit()
        add_row_layout = QtWidgets.QHBoxLayout()
        add_row_layout.addWidget(self.mat_input)
        add_row_layout.addWidget(self.weigth_input)
        add_row_layout.addWidget(self.addRow_button)
        left_box = QtWidgets.QVBoxLayout()
        left_box.addWidget(self.id_label)
        left_box.addWidget(self.data_label)
        left_box.addWidget(self.postach_name_label)
        left_box.addWidget(self.car_num_label)
        left_box.addWidget(self.brutto_label)
        left_box.addWidget(self.tara_label)
        left_box.addWidget(self.netto_label)
        left_box.addWidget(self.total_summ_label)
        left_box.addWidget(self.diff_label)
        left_box.addWidget(self.zasor_label)
        right_box = QtWidgets.QVBoxLayout()
        right_box.addWidget(self.id_value)
        right_box.addWidget(self.data_value)
        right_box.addWidget(self.postach_name)
        right_box.addWidget(self.car_num)
        right_box.addWidget(self.brutto_value)
        right_box.addWidget(self.tara_value)
        right_box.addWidget(self.netto_value)
        right_box.addWidget(self.total_summ_value)
        right_box.addWidget(self.diff_value)
        right_box.addWidget(self.zasor_value)
        # car_num_box.addStretch()
        info_box = QtWidgets.QHBoxLayout()
        info_box.addLayout(left_box)
        info_box.addLayout(right_box)
        material_box = QtWidgets.QHBoxLayout()
        material_box.addWidget(self.table)
        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(self.write_button)
        button_box.addWidget(self.split_button)
        # button_box.addWidget(self.print_button)
        button_box.addWidget(self.cancel_button)
        window_layout = QtWidgets.QVBoxLayout()
        window_layout.addLayout(info_box)
        window_layout.addLayout(material_box)
        window_layout.addLayout(add_row_layout)
        window_layout.addLayout(button_box)
        self.table.itemChanged.connect(self.changed)
        self.cancel_button.clicked.connect(self.Cancel)
        self.addRow_button.clicked.connect(self.add_row_mater)
        self.write_button.clicked.connect(self.write_to_archive)
        self.print_button.clicked.connect(self.print_check)
        self.split_button.clicked.connect(self.split)
        self.zasor_value.returnPressed.connect(self.zasor_changed)
        # vbox.addWidget(self.write_button)
        # self.write_button.clicked.connect(self.write_postach)
        central_widget.setLayout(window_layout)

    def split(self):
        print(self.result)
        self.total_summ = int(self.total_summ_value.text().replace(" кг", ""))
        print("total_summ", self.total_summ)

        new_weight = self.result[0][2] - self.total_summ
        print(new_weight)
        split_result = [[]]
        for i in list(self.result[0]):
            split_result[0].append(i)

        # self.result = [list(self.result[0])]
        print(split_result)
        split_result[0][3] = new_weight
        print("result", split_result)
        new_result = [list(self.result[0])]
        new_result[0][2] = new_weight
        self.netto = int(split_result[0][2]) - int(split_result[0][3])
        print("result2", new_result)
        print(new_weight)
        self.netto_value.setText(str(self.netto) + " кг")
        self.netto = int(self.netto_value.text().replace(" кг", ""))
        print("self.netto = ", self.netto)
        print(type(self.netto))

        if self.netto == 0:
            return
        if self.postach_edit:
            postach = self.postach_name.currentText()
        else:
            postach = self.postach_name.text()
        self.json_value = {}
        total_rows = self.table.rowCount()
        for i in range(0, total_rows):
            self.json_value[self.table.item(i, 0).text()] = {
                'weight': int(self.table.item(i, 1).text()),
                'price': float(self.table.item(i, 2).text().replace(',', '.'))
            }
        query_json = json.dumps(self.json_value, ensure_ascii=False)
        write_to_db(
            "UPDATE records SET tara = %s, material = '%s', netto = %d, postachalnik = '%s' WHERE id = %s"
            % (split_result[0][3], query_json, self.netto, postach,
               self.index))
        query = "INSERT INTO records (car_num, brutto,tara,kassir,postachalnik,material,price,is_enter,is_oplacheno,is_finished,zasor,netto,exit_time) VALUES('%s',%d,%d,'%s','%s','%s',%f,%d,%d,%d,%d,%d,now())" % (
            new_result[0][1], new_result[0][2], new_result[0][3],
            new_result[0][4], new_result[0][5], new_result[0][6],
            new_result[0][7], new_result[0][8], new_result[0][9],
            new_result[0][10], new_result[0][13],
            new_result[0][2] - new_result[0][3])
        rec_id = write_to_db(query)
        print(rec_id)
        try:
            self.changed(self.table.item(0, 1))
        except Exception as e:
            raise e
        split_result = make_request(
            "SELECT * FROM records WHERE id =%s" % rec_id)
        EditWaitForArchive(
            self, index=rec_id, result=split_result, postach_edit=1).show()
        print(self.total_summ)
        self.procDone.emit("completed")
        comm.reload_all.emit()
        # write_to_db(query)
        print("Split!!")

    # def split(self):
    #     print(self.result)
    #     new_weight = self.result[0][2] - self.total_summ
    #     new_result = [list(self.result[0])]
    #     new_result[0][2] = new_weight
    #     self.result = [list(self.result[0])]
    #     self.result[0][3] = new_weight
    #     self.netto = int(self.result[0][2]) - int(self.result[0][3])
    #     self.netto_value.setText(str(self.netto) + " кг")
    #     print(self.result)
    #     print(new_weight)
    #     if self.postach_edit:
    #         postach = self.postach_name.currentText()
    #     else:
    #         postach = self.postach_name.text()
    #     self.json_value = {}
    #     total_rows = self.table.rowCount()
    #     for i in range(0, total_rows):
    #         self.json_value[self.table.item(i, 0).text()] = {
    #             'weight': int(self.table.item(i, 1).text()),
    #             'price': float(self.table.item(i, 2).text().replace(',', '.'))
    #         }
    #     query_json = json.dumps(self.json_value, ensure_ascii=False)
    #     write_to_db(
    #         "UPDATE records SET tara = %s, material = '%s', netto = %s, postachalnik = '%s' WHERE id = %s"
    #         % (self.result[0][3], query_json, self.netto, postach, self.index))
    #     query = "INSERT INTO records (car_num, brutto,tara,kassir,postachalnik,material,price,is_enter,is_oplacheno,is_finished,zasor,netto,exit_time) VALUES('%s',%d,%d,'%s','%s','%s',%f,%d,%d,%d,%d,%d,now())" % (
    #         new_result[0][1], new_result[0][2], new_result[0][3],
    #         new_result[0][4], new_result[0][5], new_result[0][6],
    #         new_result[0][7], new_result[0][8], new_result[0][9],
    #         new_result[0][10], new_result[0][13],
    #         new_result[0][2] - new_result[0][3])
    #     rec_id = write_to_db(query)
    #     print(rec_id)
    #     try:
    #         self.changed(self.table.item(0, 1))
    #     except Exception as e:
    #         raise e
    #     split_result = make_request(
    #         "SELECT * FROM records WHERE id =%s" % rec_id)
    #     EditWaitForArchive(
    #         self, index=rec_id, result=split_result, postach_edit=1).show()
    #     print(self.total_summ)
    #     mqtt_client.publish("/reload","1")
    #     self.procDone.emit("completed")
    #     # write_to_db(query)
    #     print("Split!!")

    def zasor_changed(self):
        if self.zasor_value.text() == "":
            self.zasor = 0
            self.zasor_value.setText("0")
        else:
            try:
                self.zasor = int(self.zasor_value.text())
            except ValueError as e:
                self.zasor = 0
                self.zasor_value.setText("0")
                print(e)
        self.changed(self.table.item(0, 1))
        print(self.zasor)
        mqtt_client.publish("/reload", "1")

    # @QtCore.pyqtSlot()
    def write_to_archive(self):
        #load json from table
        self.json_value = {}
        total_rows = self.table.rowCount()
        for i in range(0, total_rows):
            self.json_value[self.table.item(i, 0).text()] = {
                'weight': int(self.table.item(i, 1).text().replace(',', '.')),
                'price': float(self.table.item(i, 2).text().replace(',', '.')),
                'trash': float(self.table.item(i, 4).text().replace(',', '.'))
            }
        print(self.json_value)
        self.total_summ = int(self.total_summ_value.text().replace(" кг", ""))
        print(self.total_summ)
        print(self.netto)
        self.diff = self.netto - self.total_summ
        print(self.diff)
        print(type(self.diff))
        query_json = json.dumps(self.json_value, ensure_ascii=False)
        if self.postach_edit:
            postach = self.postach_name.currentText()
        else:
            postach = self.postach_name.text()
        if self.diff == 0:
            write_to_db(
                "UPDATE records SET material = '%s', is_archived = 1, netto = %s, postachalnik = '%s' WHERE id = %s"
                % (query_json, self.netto, postach, self.index))
            write_to_db("UPDATE records SET zasor = %d WHERE id = %s" %
                        (self.zasor, self.index))
            self.procDone.emit("completed")
            comm.reload_all.emit()
            mqtt_client.publish("/reload", "1")
            self.close()
        elif self.diff < 0:
            QtWidgets.QMessageBox.about(self, 'Вага по даним більше ніж нетто',
                                        'Вага по даним більше ніж нетто')
            print("Вес по данным больше чем нетто")
        elif self.diff > 0:
            QtWidgets.QMessageBox.about(self, 'Ваг по даним менше ніж нетто',
                                        'Вага по данним менше ніж нетто')
            print("Вага по даним менше ніж нетто")
        #make query string
        #execute query
    def print_check(self):
        check_string = "Print test"
        self.json_value = {}
        total_rows = self.table.rowCount()
        for i in range(0, total_rows):
            self.json_value[self.table.item(i, 0).text()] = {
                'weight': int(self.table.item(i, 1).text()),
                'price': float(self.table.item(i, 2).text().replace(',', '.'))
            }
        print("==" * 20)
        print("== Номер запису", self.index)
        print("== ", self.data_value.text())
        print("== Постачальник", self.postach_name.text())
        print("== Авто", self.car_num.text())
        print("== Вага нетто ", self.netto_value.text())
        print("== Перебірка ", self.total_summ_value.text())
        print("== Засмічення", self.zasor_value.text())
        print("==" * 20)
        for key in self.json_value:
            print(
                "==", key, self.json_value[key]['weight'], "кг",
                self.json_value[key]['price'], "грн\кг",
                self.json_value[key]['weight'] * self.json_value[key]['price'],
                "кг")
        print("==" * 20)
        print_check(self.index)
        # print(check_string)
    def add_row_mater(self):
        self.table.itemChanged.disconnect(self.changed)
        new_row_material = self.mat_input.text().lower()
        result = make_request(
            "SELECT material FROM materials WHERE material='%s'" %
            new_row_material)
        print(result)
        if len(result) == 0 and new_row_material != "":
            write_to_db("INSERT INTO materials(material) VALUES('%s')" %
                        (new_row_material))
            # query = "INSERT INTO postachalniky(name,car_num) VALUES('%s','%s')" % (
            #     self.record.postachalnik, self.record.avto)
            # cur.execute(query)
            # db.commit()
            materials.append(new_row_material)
            self.mat_input_completer = QtWidgets.QCompleter(materials)
            self.mat_input_completer.setCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
            self.mat_input.setCompleter(self.mat_input_completer)
        row_count = self.table.rowCount()
        try:
            new_weight = int(self.weigth_input.text())
        except ValueError as e:
            new_weight = 0
        for i in range(0, row_count):
            if new_row_material == self.table.item(i, 0).text():
                QtWidgets.QMessageBox.about(
                    self, 'Позиція вже є',
                    'Позиція вже є у переліку')
                print("Can`t add row")
                return
        if new_row_material != "":
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0,
                               QtWidgets.QTableWidgetItem(new_row_material))
            self.table.setItem(row_count, 1,
                               QtWidgets.QTableWidgetItem(str(new_weight)))
            self.table.setItem(row_count, 2, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(row_count, 3, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(row_count, 4, QtWidgets.QTableWidgetItem("0"))
            print("New row added")
        self.changed(self.table.item(0, 1))
        self.table.itemChanged.connect(self.changed)

    def Cancel(self):
        self.close()

    def changed(self, item):
        print(self.table.rowCount())
        if item:
            if item.column() == 1:
                print(item.text(), item.column(), item.row())
                row_count = 0
                self.total_summ = 0
                total_trash = 0
                while row_count < self.table.rowCount():
                    try:
                        edit_weight = int(self.table.item(row_count, 1).text())
                        price = float(
                            self.table.item(row_count, 2).text().replace(
                                ',', '.'))
                        weight = int(self.table.item(row_count, 1).text())
                        trash = int(self.table.item(row_count, 4).text())
                        total_trash = total_trash  + trash
                        self.table.setItem(row_count, 3,
                                           QtWidgets.QTableWidgetItem(
                                               "{0:.2f}".format(
                                                   price * weight)))
                    except ValueError as e:
                        edit_weight = 0
                        self.table.setItem(row_count, 1,
                                           QtWidgets.QTableWidgetItem(str(0)))
                        print(e)
                    self.total_summ = self.total_summ + edit_weight + trash
                    row_count = row_count + 1
                self.total_summ = self.total_summ + self.zasor
                self.zasor_value.setText(str(self.zasor+total_trash))
                self.total_summ_value.setText(str(self.total_summ))
                self.diff_value.setText(str(self.netto - self.total_summ))
            elif item.column() == 0 and item.text() == "":
                print("Row removed")
                self.table.removeRow(item.row())
                try:
                    self.changed(self.table.item(0, 1))
                except Exception as e:
                    raise e
            elif item.column() == 2:
                row_count = 0
                self.total_summ = 0
                while row_count < self.table.rowCount():
                    try:
                        price = float(
                            self.table.item(row_count, 2).text().replace(
                                ',', '.'))
                        weight = int(self.table.item(row_count, 1).text())
                        self.table.setItem(row_count, 3,
                                           QtWidgets.QTableWidgetItem(
                                               "{0:.2f}".format(
                                                   price * weight)))
                        self.table.itemChanged.disconnect(self.changed)
                        self.table.setItem(row_count, 2,
                                           QtWidgets.QTableWidgetItem(
                                               "{0:.2f}".format(price)))
                        self.table.itemChanged.connect(self.changed)
                    except:
                        print("Error")
                    row_count = row_count + 1
            elif item.column() == 4:
                print("Trash changed")
                try:
                    self.changed(self.table.item(0, 1))
                except Exception as e:
                    raise e
        else:
            self.total_summ = 0
            self.total_summ_value.setText(str(self.total_summ))
            self.diff_value.setText(str(self.netto - self.total_summ))



