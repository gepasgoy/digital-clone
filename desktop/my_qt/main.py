import sys
import re
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, QObject


# ---------------- MOCK USERS ----------------
USERS = {
    "A1234567": {"password": "1234", "role": "doctor"},
    "B7654321": {"password": "admin", "role": "admin"},
}

# ---------------- UI LOADER ----------------
def load_ui(path):
    loader = QUiLoader()
    file = QFile(path)
    file.open(QFile.ReadOnly)
    ui = loader.load(file)
    file.close()
    return ui


# ---------------- MAIN WINDOW ----------------
class MainWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.ui = load_ui("Main.ui")
        self.setCentralWidget(self.ui)

        self.role = role
        self.ui.roleLabel.setText(f"Role: {role}")

        # role access
        if role != "admin":
            self.ui.adminBtn.setEnabled(False)

        # inactivity logout timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_logout)
        self.timer.start(10000)

        # reset timer on activity
        app.installEventFilter(self)

    def eventFilter(self, obj: QObject, event):
        self.timer.start(10000)
        return False

    def auto_logout(self):
        QMessageBox.warning(self, "Logout", "Неактивность > 10 сек")
        self.close()


# ---------------- SMS WINDOW ----------------
class SmsWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.ui = load_ui("Sms.ui")
        self.setCentralWidget(self.ui)

        self.role = role
        self.code = str(random.randint(1000, 9999))
        self.ui.smsLabel.setText(f"SMS код (эмуляция): {self.code}")

        self.ui.smsCheckBtn.clicked.connect(self.check)

    def check(self):
        if self.ui.smsEdit.text() == self.code:
            self.main = MainWindow(self.role)
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный код")


# ---------------- LOGIN WINDOW ----------------
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = load_ui("Login.ui")
        self.setCentralWidget(self.ui)

        self.make_captcha()
        self.ui.loginBtn.clicked.connect(self.login)

    # --- clinical captcha ---
    def make_captcha(self):
        self.answer = "гипертония"
        self.ui.captchaLabel.setText(
            "Пациент 65 лет\nАД 170/100\nГлюкоза 8.5\nДиагноз?"
        )

    def check_id(self, text):
        return re.fullmatch(r"[A-ZА-Я]\d{7}", text)

    def login(self):
        uid = self.ui.idEdit.text()
        pwd = self.ui.passwordEdit.text()
        captcha = self.ui.captchaEdit.text().lower()

        # captcha
        if captcha != self.answer:
            self.ui.statusLabel.setText("Ошибка капчи")
            return

        # id format
        if not self.check_id(uid):
            self.ui.statusLabel.setText("Неверный формат ID")
            return

        # auth
        user = USERS.get(uid)
        if not user or user["password"] != pwd:
            self.ui.statusLabel.setText("Нет доступа")
            return

        # 2FA
        self.sms = SmsWindow(user["role"])
        self.sms.show()
        self.close()


# ---------------- START ----------------
app = QApplication(sys.argv)
w = LoginWindow()
w.show()
sys.exit(app.exec())
