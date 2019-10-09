import pymysql as sql
import configparser

from PyQt5 import QtCore
from tabulate import tabulate



configParser = configparser.RawConfigParser()
configFilePath = "Weight_tools/weight.conf"
configParser.read(configFilePath)
host = configParser.get('CONFIG', 'HOST')
user = configParser.get('CONFIG', 'USER')
password = configParser.get('CONFIG', 'PASSWORD')
database = configParser.get('CONFIG', 'DATABASE')

kassiry = [""]
materials = []
postachalnik_list = []
car_list = []
our_cars_list = []
wait_for_archive_list = []

makulatura = ["5б-бн", "лоток-бн", "гільза-бн", "8в-бн"]

polymer = [
    "пе-бн", "ящик-бн", "стр-бн", "пет-бн", "пет-преформа-бн", "пет-пробка-бн",
    "етикетка", "лента-пет-бн", "пп-беги-бн", "пет-пр-бн", "пе-цв-бн",
    "пет-мікс-бн", "пе-сіp"
]

def make_request(query):
    db = sql.connect(
        host, user, password, database, use_unicode=True, charset="utf8")
    cur = db.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    db.close()
    return result


def write_to_db(query):
    db = sql.connect(
        host, user, password, database, use_unicode=True, charset="utf8")
    cur = db.cursor()
    cur.execute(query)
    cur_id = cur.lastrowid
    db.commit()
    cur.close()
    db.close()
    return cur_id


def cap_postavshik(postachalnik):
    post_list = postachalnik.split(" ")
    for i in range(len(post_list)):
        post_list[i] = post_list[i].capitalize()
    return (" ").join(post_list)


def get_check_data(doc_number):
    result = make_request("SELECT * FROM records WHERE id = %s" % doc_number)
    print(result)
    materials_json = json.loads(result[0][6])
    check_data = []
    date_record = '{0:%Y-%m-%d\n%H:%M:%S}'.format(result[0][0])
    print(date_record)
    print(type(date_record))
    total_summ = 0
    check_data.append(['Номер', doc_number])
    check_data.append(['Дата', date_record])
    check_data.append(['Постачальник', cap_postavshik(result[0][5])])
    check_data.append(['Авто', result[0][1].upper()])
    check_data.append(["Матеріали", ''])
    for key in materials_json:
        check_data.append([
            '', key,
            str(materials_json[key]['weight']) + ' кг',
            str(materials_json[key]['price']) + 'грн'
        ])
        total_summ = total_summ + (
            materials_json[key]['weight'] * materials_json[key]['price'])
    check_data.append(['Засмічення', result[0][13]])
    check_data.append(['До сплати', total_summ])
    check_data.append(['Нетто', result[0][12]])
    check_data.append(['Брутто', result[0][2]])
    check_data.append(['Тара', result[0][3]])
    check_data.append(['Касир', result[0][4]])
    return (tabulate(check_data))

def print_data(printstring):
    pfile = "check.txt"
    open(pfile, "w").write(printstring)
    print(printstring)
    win32api.ShellExecute(0, "printto", pfile,
                          u'"%s"' % win32print.GetDefaultPrinter(), ".", 0)

def print_check(doc_number):
    print_data(get_check_data(doc_number))

def get_kassiry():
    global kassiry
    kassiry = []
    print('Get kassiry')
    result = make_request("SELECT * FROM kassiry")
    for i in result:
        kassiry.append(i[0])

print('Get kassiry')
result = make_request("SELECT * FROM kassiry")
for i in result:
    kassiry.append(i[0])

print('Get material')
result = make_request("SELECT * FROM materials")
for i in result:
    materials.append(i[0].lower())

def get_postachalniky():
    global postachalnik_list
    postachalnik_list = []
    print('Get postachalniky')
    result = make_request("SELECT * FROM postachalniky")
    for i in result:
        postachalnik_list.append(i[0].lower())
    postachalnik_list.sort()
print('Get postachalniky')
result = make_request("SELECT * FROM postachalniky")
for i in result:
    postachalnik_list.append(i[0].lower())
print('Get waiting car numbers')
result = make_request("SELECT * FROM records WHERE is_finished = 0")
for i in result:
    car_list.append(i[1])
print(car_list)
print('Get our cars')
result = make_request("SELECT * FROM our_car")
for i in result:
    our_cars_list.append(i[1].lower())
print('Get waiting records')
wait_for_archive_list = make_request(
    "SELECT * FROM records WHERE is_archived = 0 AND is_finished = 1")


#mqtt section
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        client.subscribe("/vesy")
        print("Connected with code %d" % rc)
    # client.loop_start()

class Communicate(QtCore.QObject):
    reload_all = QtCore.pyqtSignal()

    def set(self,func):
        # Connect the trigger signal to a slot.
        self.reload_all.connect(func)
        print("Connect funcs to reload")
        # Emit the signal.
        # self.reload_all.emit()

