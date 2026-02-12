import sys, re, random, requests
from PySide6.QtWidgets import QApplication, QMainWindow
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
        idv = self.ui.idEdit.text()

        # критерий — формат ID
        if not re.match(r"^[A-Z]\d{7}$", idv):
            self.ui.statusLabel.setText("ID неверный")
            return

        r = requests.post(API+"/login", json={
            "mail": self.ui.mailEdit.text(),
            "password": self.ui.passEdit.text()
        })

        if r.status_code != 200:
            self.ui.statusLabel.setText("login fail")
            return

        token = r.json()["access_token"]

        me = requests.get(API+"/me",
            headers={"Authorization": f"Bearer {token}"}).json()

        self.w = Main(token, me["role"])
        self.w.show()
        self.close()


# ---------------- MAIN ----------------

class Main(QMainWindow):
    def __init__(self, token, role):
        super().__init__()
        self.ui = load_ui("Main.ui", self)
        self.token = token

        # роли
        if role != 2:
            self.ui.adminBtn.setEnabled(False)

        # 2FA
        self.sms = str(random.randint(1000,9999))
        self.ui.smsLabel.setText(self.sms)
        self.ui.smsBtn.clicked.connect(
            lambda: self.ui.smsLabel.setText(
                "OK" if self.ui.smsEdit.text()==self.sms else "ERR"
            ))

        # клиническая капча
        self.ui.captchaLabel.setText(
            "65 лет, АД 170/100, глюкоза 8.5 — диагноз?"
        )
        self.ui.captchaBtn.clicked.connect(
            lambda: self.ui.captchaLabel.setText(
                "OK" if "гипер" in self.ui.captchaEdit.text().lower() else "ERR"
            ))

        # авто-logout
        self.t = QTimer()
        self.t.timeout.connect(self.logout)
        self.t.start(10000)

        for w in self.ui.findChildren(object):
            try: w.installEventFilter(self)
            except: pass

    def eventFilter(self, *_):
        self.t.start(10000)
        return False

    def logout(self):
        try:
            requests.post(API+"/logout",
                headers={"Authorization": f"Bearer {self.token}"})
        except:
            pass
        self.l = Login()
        self.l.show()
        self.close()


# ---------------- RUN ----------------

app = QApplication(sys.argv)
w = Login()
w.show()
app.exec()