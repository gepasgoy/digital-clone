import sys, re, random, requests
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer

API = "http://127.0.0.1:8000"


def load_ui(name, parent=None):
    f = QFile(name)
    f.open(QFile.ReadOnly)
    ui = QUiLoader().load(f, parent)
    f.close()
    return ui


# ---------------- LOGIN ----------------

class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = load_ui("Login.ui", self)
        self.ui.loginBtn.clicked.connect(self.go)

    def go(self):
        r = requests.post(API+"/login", json={
            "mail": self.ui.mailEdit.text(),
            "password": self.ui.passEdit.text()
        })

        if r.status_code != 200:
            self.ui.statusLabel.setText("login fail")
            return

        token = r.json()["access_token"]

        self.v = Verify(token)
        self.v.show()
        self.close()



# ---------------- MAIN ----------------

class Verify(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.ui = load_ui("Verify.ui", self)
        self.token = token

        self.sms_ok = False
        self.captcha_ok = False

        # SMS эмуляция
        self.sms = str(random.randint(1000,9999))
        self.ui.smsLabel.setText(f"SMS код: {self.sms}")
        self.ui.smsBtn.clicked.connect(self.check_sms)

        # клиническая капча
        self.ui.captchaLabel.setText(
            "Пациент 65 лет, АД 170/100, глюкоза 8.5 — диагноз?"
        )
        self.ui.captchaBtn.clicked.connect(self.check_captcha)

    def check_sms(self):
        if self.ui.smsEdit.text() == self.sms:
            self.sms_ok = True
            self.try_open_main()


    def check_captcha(self):
        if "гипер" in self.ui.captchaEdit.text().lower():
            self.captcha_ok = True
            self.try_open_main()


    def try_open_main(self):
        if self.sms_ok and self.captcha_ok:

            me = requests.get(API+"/me",
                headers={"Authorization": f"Bearer {self.token}"}).json()

            self.m = Main(self.token, me["role"])
            self.m.show()
            self.close()




PATIENTS = [
    {"id": 1, "name": "Иванов", "age": 72},
    {"id": 2, "name": "Петров", "age": 34},
    {"id": 3, "name": "Сидоров", "age": 15},
    {"id": 4, "name": "Смирнова", "age": 67},
]


def age_tag(age):
    if age >= 60:
        return "Пожилой"
    if age < 18:
        return "Ребёнок"
    return "Взрослый"


class Main(QMainWindow):

    def __init__(self, token, role):
        super().__init__()
        self.ui = load_ui("Main.ui", self)
        self.token = token
        self.role = role

        # ---------------- РОЛИ ----------------

        if role != 2:  # admin = 2 в твоем API
            self.ui.groupExportBtn.setEnabled(False)

        # ---------------- ПАЦИЕНТ ----------------

        self.patient = PATIENTS[0]

        self.ui.patientNameLabel.setText(self.patient["name"])
        self.ui.patientAgeLabel.setText(str(self.patient["age"]))
        self.ui.tagLabel.setText(age_tag(self.patient["age"]))

        # ---------------- БЫСТРЫЕ ДЕЙСТВИЯ ----------------

        self.ui.quickPulseBtn.clicked.connect(
            lambda: print("Добавить пульс")
        )

        self.ui.quickNoteBtn.clicked.connect(
            lambda: print("Добавить заметку")
        )

        self.ui.quickAlertBtn.clicked.connect(
            lambda: print("Сигнал врачу")
        )

        # ---------------- СПИСОК ПАЦИЕНТОВ ----------------

        self.ui.patientsList.clear()

        for p in PATIENTS:
            self.ui.patientsList.addItem(
                f'{p["id"]} | {p["name"]} | {age_tag(p["age"])}'
            )

        self.ui.groupTagBtn.clicked.connect(self.group_tag)
        self.ui.groupExportBtn.clicked.connect(self.group_export)

        # ---------------- ИСТОРИЯ БОЛЕЗНИ ----------------

        # self.ui.historyTable.setRowCount(2)
        # self.ui.historyTable.setColumnCount(2)
        # self.ui.historyTable.setHorizontalHeaderLabels(
        #     ["Дата","Событие"]
        # )

        # self.ui.historyTable.setItem(0,0,QTableWidgetItem("01.02"))
        # self.ui.historyTable.setItem(0,1,QTableWidgetItem("Осмотр"))

        # ---------------- НАЗНАЧЕНИЯ ----------------

        # self.ui.assignList.addItems([
        #     "Аспирин",
        #     "Контроль АД"
        # ])

        # ---------------- ИССЛЕДОВАНИЯ ----------------

        # self.ui.researchTable.setRowCount(1)
        # self.ui.researchTable.setColumnCount(2)
        # self.ui.researchTable.setHorizontalHeaderLabels(
        #     ["Тип","Результат"]
        # )

        # self.ui.researchTable.setItem(0,0,QTableWidgetItem("Глюкоза"))
        # self.ui.researchTable.setItem(0,1,QTableWidgetItem("8.5"))

        # # ---------------- ДОКУМЕНТЫ ----------------

        # self.ui.docsList.addItems([
        #     "Эпикриз.pdf",
        #     "Анализы.pdf"
        # ])

        # ---------------- АВТОЛОГУТ ----------------

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.logout)
        # self.timer.start(10000)

        # for w in self.ui.findChildren(object):
        #     try: w.installEventFilter(self)
        #     except: pass


    # -------- групповые операции --------

    def selected_ids(self):
        ids = []
        for i in self.ui.patientsList.selectedItems():
            ids.append(i.text().split("|")[0])
        return ids

    def group_tag(self):
        print("Назначить тег:", self.selected_ids())

    def group_export(self):
        print("Экспорт:", self.selected_ids())

    # -------- авто выход --------

    # def eventFilter(self, *_):
    #     self.timer.start(10000)
    #     return False

    # def logout(self):
    #     try:
    #         requests.post(API+"/logout",
    #             headers={"Authorization":f"Bearer {self.token}"})
    #     except:
    #         pass
    #     self.l = Login()
    #     self.l.show()
    #     self.close()




# ---------------- RUN ----------------

app = QApplication(sys.argv)
w = Login()
w.show()
app.exec()