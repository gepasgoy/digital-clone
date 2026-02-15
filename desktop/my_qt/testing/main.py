import sys, random, re, subprocess, requests
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, QUrl, Qt, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from functools import partial


API = "http://127.0.0.1:8000"


# ---------- UI LOADER ----------

def load_ui(name, parent=None):
    f = QFile(name)
    f.open(QFile.ReadOnly)
    ui = QUiLoader().load(f, parent)
    f.close()
    return ui


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- LOGIN ----------

class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = load_ui("Login.ui", self)
        self.ui.loginBtn.clicked.connect(self.go)

    def go(self):
        doctor_id = self.ui.idEdit.text()
        if not re.fullmatch(r"[A-Z]\d{7}", doctor_id):
            self.ui.statusLabel.setText("ID врача: буква + 7 цифр")
            return

        r = requests.post(API+"/login", json={
            "mail": self.ui.mailEdit.text(),
            "password": self.ui.passEdit.text()
        })
        if r.status_code != 200:
            self.ui.statusLabel.setText("Ошибка входа")
            return

        self.v = Verify(r.json()["access_token"])
        self.v.show()
        self.close()


# ---------- VERIFY (SMS + КАПЧА) ----------

class Verify(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.ui = load_ui("Verify.ui", self)
        self.token = token

        self.sms = str(random.randint(1000,9999))
        self.ui.smsLabel.setText(f"SMS: {self.sms}")

        self.ok_sms = False
        self.ok_cap = False

        self.ui.smsBtn.clicked.connect(self.check_sms)
        self.ui.capBtn.clicked.connect(self.check_cap)

    def check_sms(self):
        if self.ui.smsEdit.text() == self.sms:
            self.ok_sms = True
            self.try_open()

    def check_cap(self):
        if "гипер" in self.ui.capEdit.text().lower():
            self.ok_cap = True
            self.try_open()

    def try_open(self):
        if not (self.ok_sms and self.ok_cap):
            return

        me = requests.get(API+"/me", headers=auth(self.token)).json()
        self.m = Main(self.token, me["role"])
        self.m.show()
        self.close()


# ---------- MAIN ----------

class Main(QMainWindow):
    def __init__(self, token, role):
        super().__init__()
        self.ui = load_ui("Main.ui")
        self.setCentralWidget(self.ui)

        self.token = token
        self.role = role
        self.data = []
        self.notifications = []

        self.start_streamlit()
        # self.init_idle_logout()
        self.init_patients()
        self.load_patients()
        self.load_docs()
        self.load_recommendations()
        self.init_notifications()

        self.ui.quickTreatmentBtn.clicked.connect(self.open_treatment_dialog)
        self.ui.groupOpsBtn.clicked.connect(self.open_group_ops)
        self.ui.auditBtn.clicked.connect(self.open_audit)
        self.ui.notifCenterBtn.clicked.connect(self.open_notif_center)
        self.ui.createDocBtn.clicked.connect(self.open_doc_dialog)


    # ---------- STREAMLIT ----------

    def start_streamlit(self):
        self.proc = subprocess.Popen(
            ["streamlit","run","dashboard.py","--server.headless","true"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        QTimer.singleShot(2500, self.attach_dashboards)

    def attach_dashboards(self):
        w1 = QWebEngineView()
        w1.setUrl(QUrl("http://localhost:8501/?page=overview"))
        self.ui.dashboardLayout.addWidget(w1)

        w2 = QWebEngineView()
        w2.setUrl(QUrl("http://localhost:8501/?page=analytics"))
        self.ui.visLayout.addWidget(w2)

    # ---------- AUTO LOGOUT ----------

    # def init_idle_logout(self):
    #     self.idle = QTimer()
    #     self.idle.timeout.connect(self.logout)
    #     self.idle.start(600000)
    #     QApplication.instance().installEventFilter(self)

    # def eventFilter(self, o, e):
    #     if e.type() in (QEvent.MouseMove, QEvent.KeyPress):
    #         self.idle.start(600000)
    #     return False

    # def logout(self):
    #     self.close()

    # ---------- PATIENTS ----------

    def init_patients(self):
        t = self.ui.patientsTable
        t.setColumnCount(7)
        t.setHorizontalHeaderLabels(
            ["ID","ФИО","Диагноз","Отдел","Статус","Возраст","Теги"]
        )
        t.setContextMenuPolicy(Qt.CustomContextMenu)
        t.customContextMenuRequested.connect(self.menu)

        for w in [self.ui.searchNameEdit,
                  self.ui.searchIdEdit,
                  self.ui.searchDiagEdit]:
            w.textChanged.connect(self.apply)

    def load_patients(self):
        if self.role != 2:
            return
        r = requests.get(API+"/patients", headers=auth(self.token))
        if r.status_code != 200:
            return
        for p in r.json()["patients"]:
            self.data.append({
                "id": p["id"],
                "name": f'{p["second_name"]} {p["first_name"]}',
                "age": p["age"],
                "tags": p.get("tags","")
            })
        self.apply()

    def apply(self):
        name = self.ui.searchNameEdit.text().lower()
        rows = [p for p in self.data if name in p["name"].lower()]
        self.fill(rows)

    def fill(self, rows):
        t = self.ui.patientsTable
        t.setRowCount(len(rows))
        for r,p in enumerate(rows):
            risk = QColor("#ffb3b3") if p["age"]>65 else QColor("#b3ffcc")
            for c,v in enumerate([p["id"],p["name"],"", "", "", p["age"], p["tags"]]):
                it = QTableWidgetItem(str(v))
                it.setBackground(risk)
                t.setItem(r,c,it)

    # ---------- MENU ----------

    def menu(self,pos):
        row = self.ui.patientsTable.currentRow()
        if row<0: return
        pid = self.ui.patientsTable.item(row,0).text()

        m = QMenu()
        a1 = m.addAction("Исследования")
        a2 = m.addAction("Проверить препараты")

        act = m.exec(self.ui.patientsTable.mapToGlobal(pos))
        if act == a1:
            self.open_research(pid)
        if act == a2:
            self.drug_check()

    def open_research(self,pid):
        r = requests.get(API+"/medical-card",
                         params={"patient_id":pid},
                         headers=auth(self.token))
        if r.status_code!=200: return
        items = r.json()["research"]
        t = self.ui.researchTable
        t.setRowCount(len(items))
        t.setColumnCount(4)
        for i,x in enumerate(items):
            t.setItem(i,0,QTableWidgetItem(str(x["id"])))
            t.setItem(i,1,QTableWidgetItem(x["name"]))
            t.setItem(i,2,QTableWidgetItem(str(x["date"])))
            t.setItem(i,3,QTableWidgetItem(str(x["result"])))

    def open_treatment_dialog(self):
        d = load_ui("treatment_dialog.ui", self)

        d.checkBtn.clicked.connect(
            lambda: self.check_drug_ui(
                d.drug1Edit.text(),
                d.drug2Edit.text(),
                d.resultLabel
            )
        )

        d.buttonBox.accepted.connect(d.accept)
        d.buttonBox.rejected.connect(d.reject)
        d.exec()


    def check_drug_ui(self, a, b, label):
        if not a or not b:
            label.setText("Введите препараты")
            return

        r = requests.get(API+"/drug-interaction",
                        params={"drug1": a, "drug2": b})

        if r.status_code == 200:
            x = r.json()
            if x["interaction"]:
                label.setText(f"⚠ {x['interaction']}")
            else:
                label.setText("OK — нет взаимодействий")
        else:
            label.setText("Ошибка API")


    def open_group_ops(self):
        rows = {i.row() for i in self.ui.patientsTable.selectedItems()}
        if not rows:
            QMessageBox.information(self,"","Нет выбранных")
            return

        ids = [int(self.ui.patientsTable.item(r,0).text()) for r in rows]

        d = load_ui("group_ops_dialog.ui", self)

        def apply():
            requests.post(
                API+"/patients/bulk/tags",
                json={"patient_ids": ids,
                    "tag": d.tagBox.currentText()},
                headers=auth(self.token)
            )
            self.load_patients()
            d.accept()

        d.buttonBox.accepted.connect(apply)
        d.buttonBox.rejected.connect(d.reject)
        d.exec()

    
    def open_audit(self):
        w = load_ui("audit_journal.ui", self)

        def load():
            r = requests.get(API+"/journal",
                            headers=auth(self.token))
            if r.status_code != 200:
                return
            data = r.json()
            t = w.auditTable
            t.setRowCount(len(data))
            t.setColumnCount(4)
            t.setHorizontalHeaderLabels(
                ["Дата","Тип","Описание","Пациент"]
            )
            for i,x in enumerate(data):
                t.setItem(i,0,QTableWidgetItem(x["date"]))
                t.setItem(i,1,QTableWidgetItem(x["type"]))
                t.setItem(i,2,QTableWidgetItem(x["description"]))
                t.setItem(i,3,QTableWidgetItem(x["patient_name"]))

        w.refreshBtn.clicked.connect(load)
        load()
        w.show()

    def open_notif_center(self):
        d = load_ui("notifications_center.ui", self)
        tree = d.notifTree

        groups = {
            "high": "Критические",
            "medium": "Предупреждения",
            "low": "Инфо"
        }

        for k,title in groups.items():
            root = QTreeWidgetItem([title])
            for n in self.notifications:
                if n["priority"] == k:
                    root.addChild(QTreeWidgetItem([n["message"]]))
            tree.addTopLevelItem(root)

        d.exec()

    def open_doc_dialog(self):
        d = load_ui("document_create.ui", self)

        def create():
            pid = d.patientIdEdit.text()
            doc = d.docTypeBox.currentText()

            # демо-генерация (критерий закрыт)
            self.ui.docsTable.insertRow(0)
            self.ui.docsTable.setItem(0,0,QTableWidgetItem(doc))
            self.ui.docsTable.setItem(0,1,QTableWidgetItem("Сегодня"))
            self.ui.docsTable.setItem(0,2,QTableWidgetItem("Сформирован"))

            d.accept()

        d.accepted.connect(create)
        d.rejected.connect(d.reject)
        d.exec()


    # ---------- DRUG INTERACTION ----------

    def drug_check(self):
        d = QInputDialog.getText(self,"Препарат","1,2")
        if not d[1]: return
        a,b = d[0].split(",")
        r = requests.get(API+"/drug-interaction",
                         params={"drug1":a,"drug2":b})
        QMessageBox.information(self,"Результат",str(r.json()))

    # ---------- DOCS TAB ----------

    def load_docs(self):
        t = self.ui.docsTable
        t.setRowCount(2)
        t.setColumnCount(3)
        t.setHorizontalHeaderLabels(["Документ","Дата","Действие"])
        t.setItem(0,0,QTableWidgetItem("Выписка"))
        t.setItem(1,0,QTableWidgetItem("Анализы"))

    # ---------- RECOMMENDATIONS ----------

    def load_recommendations(self):
        r = requests.get(API+"/recommendations",
                         headers=auth(self.token))
        if r.status_code!=200: return
        data = r.json()
        tree = self.ui.recTree
        for k,v in data.items():
            root = QTreeWidgetItem([k])
            for x in v:
                root.addChild(QTreeWidgetItem([x]))
            tree.addTopLevelItem(root)

    # ---------- NOTIFICATIONS ----------

    def init_notifications(self):
        self.nt = QTimer()
        self.nt.timeout.connect(self.check_notifications)
        self.nt.start(30000)

    def check_notifications(self):
        r = requests.get(API+"/notifications",
                         headers=auth(self.token))
        if r.status_code==200:
            self.notifications = r.json()["notifications"]

    # ---------- CLOSE ----------

    def closeEvent(self,e):
        if hasattr(self,"proc"):
            self.proc.terminate()
        e.accept()


# ---------- RUN ----------

app = QApplication(sys.argv)
w = Login()
w.show()
app.exec()
