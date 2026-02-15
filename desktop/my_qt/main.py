import sys, random, requests, subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMenu
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, QUrl, Qt
from PySide6.QtGui import QColor

API = "http://127.0.0.1:8000"


# ---------------- UI LOADER ----------------

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


# ---------------- VERIFY ----------------

class Verify(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.ui = load_ui("Verify.ui", self)
        self.token = token

        self.sms_ok = False
        self.captcha_ok = False

        self.sms = str(random.randint(1000,9999))
        self.ui.smsLabel.setText(f"SMS код: {self.sms}")
        self.ui.smsBtn.clicked.connect(self.check_sms)

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
            me = requests.get(
                API+"/me",
                headers={"Authorization": f"Bearer {self.token}"}
            ).json()

            self.m = Main(self.token, me["role"])
            self.m.show()
            self.close()


# ---------------- HELPERS ----------------

def age_group(age):
    if age >= 60:
        return "Пожилой"
    if age < 18:
        return "Ребёнок"
    return "Взрослый"


def risk_from_age(age):
    if age >= 65:
        return "high"
    if age >= 45:
        return "medium"
    return "low"


# ---------------- MAIN ----------------

class Main(QMainWindow):
    def __init__(self, token, role):
        super().__init__()

        self.ui = load_ui("Main.ui")
        self.setCentralWidget(self.ui)

        self.token = token
        self.role = role
        self.patients_data = []

        # ---------- STREAMLIT ----------
        self.streamlit_process = subprocess.Popen(
            [
                "streamlit",
                "run",
                "dashboard.py",
                "--server.port",
                "8501",
                "--server.headless",
                "true"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        QTimer.singleShot(3000, self.init_webview)

        # ---------- PATIENT TAB ----------
        self.init_patients_tab()
        self.load_patients_from_api()
        self.init_quick_actions()


    # ---------- STREAMLIT VIEW ----------

    def init_webview(self):
        self.web = QWebEngineView(self)
        self.web.setUrl(QUrl("http://localhost:8501"))

        self.ui.dashboardLayout.addWidget(self.web)


    # ---------- PATIENTS TAB ----------

    def init_patients_tab(self):
        ui = self.ui

        ui.patientsTable.setColumnCount(6)
        ui.patientsTable.setHorizontalHeaderLabels(
            ["ID","ФИО","Диагноз","Отделение","Статус","Возраст"]
        )

        ui.deptBox.addItems(["Все"])
        ui.statusBox.addItems(["Все"])
        ui.ageBox.addItems(["Все","Ребёнок","Взрослый","Пожилой"])

        # signals → один метод
        for w in [
            ui.searchNameEdit,
            ui.searchIdEdit,
            ui.searchDiagEdit
        ]:
            w.textChanged.connect(self.apply_filters)

        ui.deptBox.currentTextChanged.connect(self.apply_filters)
        ui.statusBox.currentTextChanged.connect(self.apply_filters)
        ui.ageBox.currentTextChanged.connect(self.apply_filters)

        ui.patientsTable.setContextMenuPolicy(Qt.CustomContextMenu)
        ui.patientsTable.customContextMenuRequested.connect(self.patient_menu)


    def init_quick_actions(self):
        ui = self.ui

        ui.qaNewTreatmentBtn.clicked.connect(self.qa_new_treatment)
        ui.qaVisitBtn.clicked.connect(self.qa_visit)
        ui.qaResearchBtn.clicked.connect(self.qa_research)
        ui.qaEpicrisisBtn.clicked.connect(self.qa_epicrisis)


    # ---------- LOAD FROM API ----------

    def load_patients_from_api(self):
        if self.role != 2:
            return

        r = requests.get(
            API+"/patients",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if r.status_code != 200:
            return

        data = r.json()["patients"]

        self.patients_data = []
        for p in data:
            self.patients_data.append({
                "id": p["id"],
                "name": f'{p["second_name"]} {p["first_name"]} {p["patronomyc"]}',
                "diag": "—",
                "dept": "—",
                "status": "—",
                "age": p["age"],
                "risk": risk_from_age(p["age"])
            })

        self.apply_filters()

    # ---------- FILTER ----------

    def apply_filters(self):
        ui = self.ui
        rows = []

        for p in self.patients_data:

            if ui.searchNameEdit.text().lower() not in p["name"].lower():
                continue

            if ui.searchIdEdit.text() and ui.searchIdEdit.text() != str(p["id"]):
                continue

            if ui.searchDiagEdit.text().lower() not in p["diag"].lower():
                continue

            ag = age_group(p["age"])
            if ui.ageBox.currentText() != "Все" and ag != ui.ageBox.currentText():
                continue

            rows.append(p)

        self.fill_table(rows)

    # ---------- TABLE ----------

    def fill_table(self, data):
        t = self.ui.patientsTable
        t.setRowCount(len(data))

        colors = {
            "high": QColor("#ffb3b3"),
            "medium": QColor("#ffe0b3"),
            "low": QColor("#b3ffcc")
        }

        for r,p in enumerate(data):
            vals = [p["id"],p["name"],p["diag"],p["dept"],p["status"],p["age"]]

            for c,val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setBackground(colors[p["risk"]])
                t.setItem(r,c,item)

        t.resizeColumnsToContents()

    # ---------- CONTEXT MENU ----------

    def fill_history(self, items):
        t = self.ui.historyTable
        t.setColumnCount(1)
        t.setHorizontalHeaderLabels(["Нет данных"])
        t.setRowCount(0)


    def fill_treatments(self, items):
        t = self.ui.treatmentTable
        t.setColumnCount(1)
        t.setHorizontalHeaderLabels(["Нет данных"])
        t.setRowCount(0)


    def fill_research(self, items):
        t = self.ui.researchTable

        t.setColumnCount(4)
        t.setHorizontalHeaderLabels(["ID","Название","Дата","Результат"])
        t.setRowCount(len(items))

        for r,x in enumerate(items):
            t.setItem(r,0,QTableWidgetItem(str(x["id"])))
            t.setItem(r,1,QTableWidgetItem(x["name"]))
            t.setItem(r,2,QTableWidgetItem(str(x["date"])))
            t.setItem(r,3,QTableWidgetItem(str(x["result"])))

        t.resizeColumnsToContents()


    def open_patient_tab(self, pid, mode):

        r = requests.get(
            API + "/medical-card",
            params={"patient_id": pid},
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if r.status_code != 200:
            print("medical-card error", r.text)
            return

        data = r.json()

        if mode == "research":
            self.fill_research(data["research"])
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_research)

        elif mode == "treat":
            # у тебя treatments пока закомментированы в API
            self.fill_treatments([])
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_treatments)

        elif mode == "history":
            # visits пока нет — заглушка
            self.fill_history([])
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_history)


    def patient_menu(self, pos):
        table = self.ui.patientsTable
        row = table.currentRow()
        if row < 0:
            return

        pid = int(table.item(row,0).text())

        menu = QMenu()

        a_hist = menu.addAction("История болезней")
        a_treat = menu.addAction("Назначения")
        a_res = menu.addAction("Исследования")

        act = menu.exec(table.mapToGlobal(pos))

        if act == a_hist:
            self.open_patient_tab(pid, "history")

        elif act == a_treat:
            self.open_patient_tab(pid, "treat")

        elif act == a_res:
            self.open_patient_tab(pid, "research")

    # ---------- FAST ACTIONS ----------

    def get_selected_patient_id(self):
        t = self.ui.patientsTable
        row = t.currentRow()
        if row < 0:
            print("Пациент не выбран")
            return None
        return int(t.item(row,0).text())

    def qa_new_treatment(self):
        pid = self.get_selected_patient_id()
        if not pid: return
        print("назначение для", pid)

    def qa_visit(self):
        pid = self.get_selected_patient_id()
        if not pid: return  
        print("прием для", pid)

    def qa_epicrisis(self):
        pid = self.get_selected_patient_id()
        if not pid: return
        print("эпикриз для", pid)

    def qa_research(self):
        pid = self.get_selected_patient_id()
        if not pid: return

        print("исследование добавлено")


    # ---------- API ACTIONS ----------

    def open_medical_card(self, pid):
        r = requests.get(
            API+"/medical-card",
            params={"patient_id": pid},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("card:", r.status_code)

    def send_pulse(self, pid):
        requests.post(
            API+"/pulse-monitoring",
            json={"value": 72, "patient_id": int(pid)},
            headers={"Authorization": f"Bearer {self.token}"}
        )

    def send_complain(self, pid):
        requests.post(
            API+"/sub_complains",
            json={"PatientId": int(pid), "Description": "Тестовая жалоба"},
            headers={"Authorization": f"Bearer {self.token}"}
        )

    # ---------- CLOSE ----------

    def closeEvent(self, event):
        if hasattr(self, "streamlit_process"):
            self.streamlit_process.terminate()
        event.accept()


# ---------------- RUN ----------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Проверяем аргументы командной строки
    if "--test" in sys.argv:
        # Тестовый режим
        token = "test_token"
        role = 2
        w = Main(token, role)
    else:
        # Обычный режим
        w = Login()
    
    w.show()
    app.exec()