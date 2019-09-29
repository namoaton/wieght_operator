from Weight_tools.tools import *
from PyQt5 import QtCore, QtGui, QtWidgets


class AddCar(QtWidgets.QMainWindow):
    procDone = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Додати машину")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
        self.car_num_label = QtWidgets.QLabel('Номер авто ')
        self.car_num_label.setFont(self.newfont)
        self.car_num = QtWidgets.QLineEdit()
        self.car_num.setFont(self.newfont)
        self.write_button = QtWidgets.QPushButton('Додати')
        self.write_button.setFont(self.newfont)
        car_box = QtWidgets.QHBoxLayout()
        car_box.addStretch()
        car_box.addWidget(self.car_num_label)
        car_box.addWidget(self.car_num)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(car_box)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.write_car_num)
        central_widget.setLayout(vbox)

    def write_car_num(self):
        car_num = self.car_num.text()
        if car_num != "":
            write_to_db("INSERT INTO our_car(car_num) VALUES('%s')" %
                        (car_num))
            # query = "INSERT INTO our_car(car_num) VALUES('%s')" % (car_num)
            # cur.execute(query)
            # db.commit()
            print(" Додати ", car_num)
            self.procDone.emit()
            # comm.reload_all.emit()
            self.close()

