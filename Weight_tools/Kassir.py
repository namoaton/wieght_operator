from Weight_tools.tools import *

from PyQt5 import QtWidgets, QtCore, QtGui


class KassiryWindows(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Кассиры")
        result = make_request("SELECT * FROM kassiry ")
        print(result)
        postachalnik_num = len(result)
        print(postachalnik_num)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QtWidgets.QGridLayout()
        self.central_widget.setLayout(self.grid_layout)
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setRowCount(postachalnik_num)
        self.table.setHorizontalHeaderLabels(["Кассир", "Телефон"])
        self.table.horizontalHeaderItem(0).setToolTip("Кассир ")
        self.table.horizontalHeaderItem(1).setToolTip("Телефон ")
        self.table.horizontalHeaderItem(0).setTextAlignment(
            QtCore.Qt.AlignRight)
        self.table.horizontalHeaderItem(1).setTextAlignment(
            QtCore.Qt.AlignRight)
        counter = 0
        for i in result:
            print(i)
            self.table.setItem(counter, 0,
                               QtWidgets.QTableWidgetItem(result[counter][0]))
            self.table.setItem(counter, 1,
                               QtWidgets.QTableWidgetItem(result[counter][1]))
            counter = counter + 1
        self.table.resizeColumnsToContents()
        self.table.itemChanged.connect(self.changed)
        self.grid_layout.addWidget(self.table, 0, 0)

    def changed(self, item):
        result = make_request("SELECT * FROM kassiry ")
        print(result[item.row()])
        if item.column() == 0:
            write_to_db("UPDATE kassiry SET kassir = '%s' WHERE id = %d  " %
                        (item.text(), result[item.row()][2]))
        # query = "UPDATE kassiry SET kassir = '%s' WHERE id = %d  " % (
        #     item.text(), result[item.row()][2])
        # cur.execute(query)
        # db.commit()
        if item.column() == 1:
            write_to_db("UPDATE kassiry SET phone = '%s' WHERE id = %d  " %
                        (item.text(), result[item.row()][2]))
        # query = "UPDATE kassiry SET phone = '%s' WHERE id = %d  " % (
        #     item.text(), result[item.row()][2])
        # cur.execute(query)
        # db.commit()
        print(item.text(), item.column(), item.row())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.table.setRowCount(0)
            self.table.itemChanged.disconnect(self.changed)
            result = make_request("SELECT * FROM kassiry ")
            print(result)
            postachalnik_num = len(result)
            print(postachalnik_num)
            self.central_widget.setLayout(self.grid_layout)
            self.table.setColumnCount(2)
            self.table.setRowCount(postachalnik_num)
            self.table.setHorizontalHeaderLabels(["Кассир", "Телефон"])
            self.table.horizontalHeaderItem(0).setToolTip("Кассир ")
            self.table.horizontalHeaderItem(1).setToolTip("Телефон ")
            self.table.horizontalHeaderItem(0).setTextAlignment(
                QtCore.Qt.AlignRight)
            self.table.horizontalHeaderItem(1).setTextAlignment(
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
                counter = counter + 1
            self.table.resizeColumnsToContents()
            self.table.itemChanged.connect(self.changed)


class DodatyKassira(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Додати касира")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        self.kassir_label = QtWidgets.QLabel('ФІО ')
        self.kassir_label.setFont(self.newfont)
        self.kassir = QtWidgets.QLineEdit()
        self.kassir.setFont(self.newfont)
        self.phone_label = QtWidgets.QLabel('Телефон')
        self.phone_label.setFont(self.newfont)
        self.phone = QtWidgets.QLineEdit()
        self.phone.setFont(self.newfont)
        self.write_button = QtWidgets.QPushButton('Додати')
        self.write_button.setFont(self.newfont)
        kassir_box = QtWidgets.QHBoxLayout()
        kassir_box.addStretch()
        kassir_box.addWidget(self.kassir_label)
        kassir_box.addWidget(self.kassir)
        phone_box = QtWidgets.QHBoxLayout()
        phone_box.addWidget(self.phone_label)
        phone_box.addWidget(self.phone)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(kassir_box)
        vbox.addLayout(phone_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.write_kassir)
        central_widget.setLayout(vbox)

    def write_kassir(self):
        phone = self.phone.text()
        kassir = self.kassir.text()
        if kassir != "":
            write_to_db("INSERT INTO kassiry(kassir,phone) VALUES('%s','%s')" %
                        (kassir, phone))
            # query = "INSERT INTO kassiry(kassir,phone) VALUES('%s','%s')" % (
            #     kassir, phone)
            # cur.execute(query)
            # db.commit()
            print(" Додати ", kassir)
