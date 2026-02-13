import sys, re, random, requests
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer

import subprocess
import time
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


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


# ---------------- MAIN ----------------

class Main(QMainWindow):
    def __init__(self, token, role):
        super().__init__()

        self.ui = load_ui("Main.ui")
        self.setCentralWidget(self.ui)

        self.token = token
        self.role = role

        # --- Streamlit процесс ---
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

        # даем серверу подняться
        QTimer.singleShot(2500, self.init_webview)

    def init_webview(self):
        # Используем существующий QWebEngineView из UI
        web_view = self.ui.webEngineView
        web_view.setUrl(QUrl("http://localhost:8501"))

    def closeEvent(self, event):
        # корректно убиваем streamlit при закрытии окна
        if hasattr(self, "streamlit_process"):
            self.streamlit_process.terminate()
        event.accept()


# ---------------- RUN ----------------

app = QApplication(sys.argv)
w = Login()
w.show()
app.exec()