import configparser
import socket
import time
import paho.mqtt.client as mqtt
from threading import Thread
from PyQt5 import QtGui
from Weight_tools.tools import Communicate
import configparser
# from weights import comm

# Create conf file in  weight.conf
# with  such content

# [CONFIG]
# DATABASE = db_name
# USER = db_username
# PASSWORD= db_password
# HOST = ip address of db
configParser = configparser.RawConfigParser()
configFilePath = "Weight_tools/weight.conf"
configParser.read(configFilePath)
host = configParser.get('CONFIG', 'HOST')
MQTT_USER = configParser.get('CONFIG', 'MQTT_USER')
MQTT_PASSWORD = configParser.get('CONFIG', 'MQTT_PASSWORD')
MQTT_CLIENT = configParser.get('CONFIG', 'MQTT_CLIENT')
UDP_IP = configParser.get('CONFIG', 'UDP_IP')
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        client.subscribe("/vesy")
        print("Connected with code %d" % rc)

mqtt_client = mqtt.Client(MQTT_CLIENT)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.connect(host,port=1883, keepalive=60)

configParser = configparser.RawConfigParser()
configFilePath = "Weight_tools/weight.conf"
configParser.read(configFilePath)

UDP_PORT = int(configParser.get('CONFIG', 'UDP_PORT'))

class ReadWeightThread(Thread):
    def __init__(self, lcd_screen):
        global mqtt_client
        Thread.__init__(self)
        self.sock = socket.socket(
            socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDPo
        # self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #  uncomment below to work with weights!!!!!!!!!!!!!!!!!!!!!!!!!
        # self.sock.bind((UDP_IP, UDP_PORT))

        # procDone = QtCore.pyqtSignal(str)
        host_display = '192.168.1.177'
        port_display = 8888
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.daemon = True
        self.lcd_screen = lcd_screen
        mqtt_client.subscribe("/vesy")
        mqtt_client.subscribe("/reload")
        mqtt_client.on_message = self.on_message
        mqtt_client.loop_start()
        self.start()

    def on_message(self, client, userdata, message):
        # time.sleep(1)
        print("Topic: " + str(message.topic))
        print("Message: " + str(message.payload))
        print("received message =", str(message.payload.decode("utf-8")))
        print(str(message.topic))
        if str(message.topic) == "/vesy":
            self.lcd_screen.display(str(message.payload.decode("utf-8")))
            self.lcd_signal.emit(str(message.payload.decode("utf-8")))
        if str(message.topic) == "/reload":
            Communicate.reload_all.emit()

    def run(self):
        print("Mqtt init ok!")
        mqtt_client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=True)

        while True:
            # data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            # w = int(
            #     str(data).replace(":", "").replace("'", "").replace("b", ""))
            # print("received message:", str(data).replace(":", ""))
            # self.lcd_screen.display(w)
            # mqtt_client.loop_start()
            # self.lcd_screen.display(read_weight())
            # self.mqtt_client.loop()
            # for a  in range(1000):
            #   self.lcd_screen.display(a)
            time.sleep(1)


class EditThread(Thread):
    def __init__(self, table_view):
        Thread.__init__(self)
        self.daemon = True
        self.table_view = table_view
        # mqtt_client.on_message = self.on_message
        # mqtt_client.loop_stop()
        # mqtt_client.subscribe("/edit_record")
        # mqtt_client.loop_start()

    def on_message(self, client, userdata, message):
        time.sleep(1)
        mess_txt = str(message.payload.decode("utf-8"))
        print(" rec received message =", mess_txt)
        # locked_itemt  = self.table_view.item(0,0)
        # locked_itemt.setBackground(QtGui.QColor(125,125,125))
        self.set_lock_color(mess_txt)
        print(self.table_view.item(0, 0).text())

    def set_lock_color(self, mess_txt):
        row_count = self.table_view.rowCount()
        if mess_txt == "0":
            for row in range(row_count):
                self.set_raw_color(row, QtGui.QColor(255, 255, 255))
            return
        for row in range(row_count):
            if (self.table_view.item(row, 0).text() == mess_txt):
                self.set_raw_color(row, QtGui.QColor(125, 125, 125))
            self.table_view.setVisible(False)
            self.table_view.setVisible(True)

    def set_raw_color(self, row, color):
        for column in range(self.table_view.columnCount()):
            self.table_view.item(row, column).setBackground(color)
