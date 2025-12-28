import tkinter as tk
from tkinter import ttk, messagebox
import re
from auth.captcha import MedicalCaptcha
from auth.two_fa import TwoFactorAuth


class LoginWindow:
    def __init__(self, parent, login_callback):
        self.parent = parent
        self.login_callback = login_callback
        self.window = None

    def show(self):
        """Показать окно входа"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Вход в медицинскую систему")
        self.window.geometry("400x300")
        self.window.transient(self.parent)
        self.window.grab_set()

        # Центрирование окна
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов окна входа"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Врачебный ID
        ttk.Label(main_frame, text="Врачебный ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.id_var = tk.StringVar()
        id_entry = ttk.Entry(main_frame, textvariable=self.id_var, width=20)
        id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        id_entry.focus()

        # Пароль
        ttk.Label(main_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var,
                                   show="*", width=20)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Кнопка входа
        login_btn = ttk.Button(main_frame, text="Войти", command=self.attempt_login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=20)

        # Подсказка формата ID
        help_label = ttk.Label(main_frame, text="Формат ID: буква + 7 цифр (например: A1234567)",
                               font=("Arial", 8), foreground="gray")
        help_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Настройка расширения колонок
        main_frame.columnconfigure(1, weight=1)

    def attempt_login(self):
        """Попытка входа в систему"""
        doctor_id = self.id_var.get().strip()
        password = self.password_var.get()

        # Проверка формата врачебного ID
        if not self.validate_doctor_id(doctor_id):
            messagebox.showerror("Ошибка", "Неверный формат врачебного ID!\nФормат: буква + 7 цифр")
            return

        # Проверка пароля (заглушка)
        if not password:
            messagebox.showerror("Ошибка", "Введите пароль")
            return

        # Медицинская капча
        if not MedicalCaptcha(self.window).verify():
            return

        # Двухфакторная аутентификация
        if not TwoFactorAuth(self.window).verify():
            return

        # Успешный вход
        user_data = {
            'user_id': doctor_id,
            'role': self.determine_role(doctor_id)
        }

        self.window.destroy()
        self.login_callback(user_data)

    def validate_doctor_id(self, doctor_id):
        """Проверка формата врачебного ID"""
        pattern = r'^[A-Za-z]\d{7}$'
        return bool(re.match(pattern, doctor_id))

    def determine_role(self, doctor_id):
        """Определение роли пользователя (заглушка)"""
        roles = {
            'A': 'admin',
            'B': 'doctor',
            'C': 'nurse'
        }
        first_char = doctor_id[0].upper()
        return roles.get(first_char, 'doctor')