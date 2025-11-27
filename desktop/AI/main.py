import tkinter as tk
from tkinter import ttk, messagebox
from auth.login import LoginWindow
from ui.main_window import MainWindow
from utils.inactivity_timer import InactivityTimer
from utils.audit_logger import AuditLogger


class MedicalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Медицинская система")
        self.root.geometry("1200x800")

        self.audit_logger = AuditLogger()
        self.inactivity_timer = InactivityTimer(self.root, self.logout, timeout=1000000)

        self.current_user = None
        self.user_role = None

        self.show_login()

    def show_login(self):
        """Показать окно входа"""
        login = LoginWindow(self.root, self.login_callback)
        login.show()

    def login_callback(self, user_data):
        """Обработка успешного входа"""
        self.current_user = user_data['user_id']
        self.user_role = user_data['role']

        self.audit_logger.log("LOGIN", f"User {self.current_user} logged in")
        self.inactivity_timer.start()

        self.show_main_window()

    def show_main_window(self):
        """Показать главное окно приложения"""
        self.main_window = MainWindow(self.root, self.current_user, self.user_role,
                                      self.audit_logger, self.inactivity_timer)
        self.main_window.show()

    def logout(self):
        """Выход из системы"""
        if self.current_user:
            self.audit_logger.log("LOGOUT", f"User {self.current_user} logged out")

        self.current_user = None
        self.user_role = None
        self.inactivity_timer.stop()

        if hasattr(self, 'main_window'):
            self.main_window.hide()

        self.show_login()

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MedicalApp()
    app.run()