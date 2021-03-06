from PyQt5 import QtCore, QtWidgets, QtGui

from Weight_tools.Record import Record
from Weight_tools.WaitEditor import EditWaitForArchive
from Weight_tools.tools import *


class DodatyPostachalnika(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Додати постачльника")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        self.car_num_label = QtWidgets.QLabel('Номер авто')
        self.car_num_label.setFont(self.newfont)
        self.car_num = QtWidgets.QLineEdit()
        self.car_num.setFont(self.newfont)
        self.postach_name_label = QtWidgets.QLabel('Постачальник')
        self.postach_name_label.setFont(self.newfont)
        self.postach_name = QtWidgets.QLineEdit()
        self.postach_name.setFont(self.newfont)
        self.phone_label = QtWidgets.QLabel('Телефон')
        self.phone_label.setFont(self.newfont)
        self.phone = QtWidgets.QLineEdit()
        self.phone.setFont(self.newfont)
        self.contact_label = QtWidgets.QLabel('Контакт')
        self.contact_label.setFont(self.newfont)
        self.contact = QtWidgets.QLineEdit()
        self.contact.setFont(self.newfont)
        self.write_button = QtWidgets.QPushButton('Додати')
        self.write_button.setFont(self.newfont)
        car_num_box = QtWidgets.QHBoxLayout()
        car_num_box.addStretch()
        car_num_box.addWidget(self.car_num_label)
        car_num_box.addWidget(self.car_num)
        postach_name_box = QtWidgets.QHBoxLayout()
        postach_name_box.addWidget(self.postach_name_label)
        postach_name_box.addWidget(self.postach_name)
        phone_box = QtWidgets.QHBoxLayout()
        phone_box.addWidget(self.phone_label)
        phone_box.addWidget(self.phone)
        contact_box = QtWidgets.QHBoxLayout()
        contact_box.addWidget(self.contact_label)
        contact_box.addWidget(self.contact)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(car_num_box)
        vbox.addLayout(postach_name_box)
        vbox.addLayout(phone_box)
        vbox.addLayout(contact_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.write_postach)
        central_widget.setLayout(vbox)

    def write_postach(self):
        postach = self.postach_name.text()
        phone = self.phone.text()
        contact = self.contact.text()
        car_num = self.car_num.text()
        if postach != "":
            write_to_db(
                "INSERT INTO postachalniky(name,phone,contact,car_num) VALUES('%s','%s','%s','%s')"
                % (postach, phone, contact, car_num))



class PostachalnikiWindows(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(750, 180))
        self.setWindowTitle("Поставщики")
        result = make_request("SELECT * FROM postachalniky ")
        # print(result)
        postachalnik_num = len(result)
        print(postachalnik_num)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QtWidgets.QGridLayout()
        self.central_widget.setLayout(self.grid_layout)
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(postachalnik_num)
        self.table.setHorizontalHeaderLabels(
            ["Поставщик", "Телефон", "Контакт", "Номер авто"])
        self.table.horizontalHeaderItem(0).setToolTip("Поставщик ")
        self.table.horizontalHeaderItem(1).setToolTip("Телефон ")
        self.table.horizontalHeaderItem(2).setToolTip("Контакт ")
        self.table.horizontalHeaderItem(3).setToolTip("Номер авто ")
        self.table.horizontalHeaderItem(0).setTextAlignment(
            QtCore.Qt.AlignLeft)
        self.table.horizontalHeaderItem(1).setTextAlignment(
            QtCore.Qt.AlignHCenter)
        self.table.horizontalHeaderItem(2).setTextAlignment(
            QtCore.Qt.AlignRight)
        self.table.horizontalHeaderItem(3).setTextAlignment(
            QtCore.Qt.AlignRight)
        counter = 0
        for i in result:
            # print(i)
            self.table.setItem(counter, 0,
                               QtWidgets.QTableWidgetItem(result[counter][0]))
            self.table.setItem(counter, 1,
                               QtWidgets.QTableWidgetItem(result[counter][1]))
            self.table.setItem(counter, 2,
                               QtWidgets.QTableWidgetItem(result[counter][2]))
            self.table.setItem(counter, 3,
                               QtWidgets.QTableWidgetItem(result[counter][3]))
            counter = counter + 1
        self.table.resizeColumnsToContents()
        self.table.itemChanged.connect(self.changed)
        self.grid_layout.addWidget(self.table, 0, 0)

    def changed(self, item):
        result = make_request("SELECT * FROM postachalniky ")
        print(result[item.row()])
        if item.column() == 0:
            write_to_db(
                "UPDATE postachalniky SET name = '%s' WHERE id = %d  " %
                (item.text(), result[item.row()][4]))
        # query = "UPDATE postachalniky SET name = '%s' WHERE id = %d  " % (
        #     item.text(), result[item.row()][4])
        # cur.execute(query)
        # db.commit()
        if item.column() == 1:
            write_to_db(
                "UPDATE postachalniky SET phone = '%s' WHERE id = %d  " %
                (item.text(), result[item.row()][4]))
        # query = "UPDATE postachalniky SET phone = '%s' WHERE id = %d  " % (
        #     item.text(), result[item.row()][4])
        # cur.execute(query)
        # db.commit()
        if item.column() == 2:
            write_to_db(
                "UPDATE postachalniky SET contact = '%s' WHERE id = %d  " %
                (item.text(), result[item.row()][4]))
        #     query = "UPDATE postachalniky SET contact = '%s' WHERE id = %d  " % (
        #         item.text(), result[item.row()][4])
        #     cur.execute(query)
        #     db.commit()
        if item.column() == 3:
            write_to_db(
                "UPDATE postachalniky SET car_num = '%s' WHERE id = %d  " %
                (item.text(), result[item.row()][4]))
        # query = "UPDATE postachalniky SET car_num = '%s' WHERE id = %d  " % (
        #     item.text(), result[item.row()][4])
        # cur.execute(query)
        # db.commit()
        print(item.text(), item.column(), item.row())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.table.setRowCount(0)
            self.table.itemChanged.disconnect(self.changed)
            result = make_request("SELECT * FROM postachalniky ")
            print(result)
            postachalnik_num = len(result)
            print(postachalnik_num)
            self.central_widget.setLayout(self.grid_layout)
            self.table.setColumnCount(4)
            self.table.setRowCount(postachalnik_num)
            self.table.setHorizontalHeaderLabels(
                ["Поставщик", "Телефон", "Контакт", "Номер авто"])
            self.table.horizontalHeaderItem(0).setToolTip("Поставщик ")
            self.table.horizontalHeaderItem(1).setToolTip("Телефон ")
            self.table.horizontalHeaderItem(2).setToolTip("Контакт ")
            self.table.horizontalHeaderItem(3).setToolTip("Номер авто ")
            self.table.horizontalHeaderItem(0).setTextAlignment(
                QtCore.Qt.AlignLeft)
            self.table.horizontalHeaderItem(1).setTextAlignment(
                QtCore.Qt.AlignHCenter)
            self.table.horizontalHeaderItem(2).setTextAlignment(
                QtCore.Qt.AlignRight)
            self.table.horizontalHeaderItem(3).setTextAlignment(
                QtCore.Qt.AlignRight)
            counter = 0
            for i in result:
                # print(i)
                self.table.setItem(counter, 0,
                                   QtWidgets.QTableWidgetItem(
                                       result[counter][0]))
                self.table.setItem(counter, 1,
                                   QtWidgets.QTableWidgetItem(
                                       result[counter][1]))
                self.table.setItem(counter, 2,
                                   QtWidgets.QTableWidgetItem(
                                       result[counter][2]))
                self.table.setItem(counter, 3,
                                   QtWidgets.QTableWidgetItem(
                                       result[counter][3]))
                counter = counter + 1
            self.table.resizeColumnsToContents()
            self.table.itemChanged.connect(self.changed)

class RemovePostachalnik(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        global postachalnik_list
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Видалити касира")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        self.postachalnik_label = QtWidgets.QLabel('ФІО ')
        self.postachalnik_label.setFont(self.newfont)
        get_postachalniky()
        self.postachalnik = QtWidgets.QComboBox()
        self.postachalnik.setFont(self.newfont)
        self.postachalnik.addItems(postachalnik_list)
        self.write_button = QtWidgets.QPushButton('Видалити')
        self.write_button.setFont(self.newfont)
        postachalnik_box = QtWidgets.QHBoxLayout()
        postachalnik_box.addStretch()
        postachalnik_box.addWidget(self.postachalnik_label)
        postachalnik_box.addWidget(self.postachalnik)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(postachalnik_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.remove_postachalnik)
        central_widget.setLayout(vbox)

    def reload_postachalnik(self):
        get_postachalniky()
        global postachalnik_list
        self.postachalnik.clear()
        self.postachalnik.addItems(postachalnik_list)

    def show(self):
        super().show()
        self.reload_postachalnik()

    def remove_postachalnik(self):
        global postachalniky
        postachalnik = self.postachalnik.currentText()
        print("Remove postachalnik ", postachalnik)
        if postachalnik != "":
            query = "DELETE FROM postachalniky WHERE name='%s'" % postachalnik
            print(query)
            print(postachalnik)
            write_to_db(query)
            Record.comm.reload_all.emit()
            self.reload_postachalnik()

class PostachEditRecord(QtWidgets.QMainWindow):
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
        self.write_button = QtWidgets.QPushButton('Редагувати')
        self.write_button.setFont(self.newfont)
        num_box = QtWidgets.QHBoxLayout()
        num_box.addStretch()
        num_box.addWidget(self.num_label)
        num_box.addWidget(self.num)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(num_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.edit)
        central_widget.setLayout(vbox)

    def edit(self):
        try:
            num = int(self.num.text())
            print(num)
            if num:
                r = make_request("SELECT * FROM records WHERE id =%s" % num)
                edit_rec =EditWaitForArchive(self,result = r,postach_edit=1,index=num)
                edit_rec.show()
                Record.comm.reload_all.emit()
                # self.hide()
        except Exception as e:
            raise e
