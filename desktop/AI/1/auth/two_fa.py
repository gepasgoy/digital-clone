import tkinter as tk
from tkinter import ttk, messagebox
import random


class TwoFactorAuth:
    def __init__(self, parent):
        self.parent = parent
        self.verified = False
        self.sms_code = str(random.randint(100000, 999999))

    def verify(self):
        """Проверка двухфакторной аутентификации"""
        self.show_2fa_window()
        return self.verified

    def show_2fa_window(self):
        """Показать окно двухфакторной аутентификации"""
        auth_window = tk.Toplevel(self.parent)
        auth_window.title("Двухфакторная аутентификация")
        auth_window.geometry("350x200")
        auth_window.transient(self.parent)
        auth_window.grab_set()

        main_frame = ttk.Frame(auth_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Информация о SMS
        info_text = f"На ваш номер отправлен SMS с кодом подтверждения.\nТестовый код: {self.sms_code}"
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.CENTER)
        info_label.pack(pady=10)

        # Поле для ввода кода
        ttk.Label(main_frame, text="SMS код:").pack(anchor=tk.W, pady=(20, 5))
        self.code_var = tk.StringVar()
        code_entry = ttk.Entry(main_frame, textvariable=self.code_var, width=10, font=("Arial", 12))
        code_entry.pack(pady=5)
        code_entry.focus()

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Подтвердить",
                   command=lambda: self.verify_code(auth_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=auth_window.destroy).pack(side=tk.LEFT, padx=5)

        auth_window.wait_window()

    def verify_code(self, window):
        """Проверка SMS кода"""
        if self.code_var.get() == self.sms_code:
            self.verified = True
            window.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный SMS код")