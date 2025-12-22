import tkinter as tk
from tkinter import ttk, messagebox


class MedicalCaptcha:
    def __init__(self, parent):
        self.parent = parent
        self.verified = False

    def verify(self):
        """Проверка медицинской капчи"""
        self.show_captcha_window()
        return self.verified

    def show_captcha_window(self):
        """Показать окно медицинской капчи"""
        captcha_window = tk.Toplevel(self.parent)
        captcha_window.title("Медицинская проверка")
        captcha_window.geometry("500x400")
        captcha_window.transient(self.parent)
        captcha_window.grab_set()

        main_frame = ttk.Frame(captcha_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Медицинский кейс
        case_text = """Клинический случай:

Пациент 65 лет
Артериальное давление: 170/100 мм рт.ст.
Глюкоза крови: 8.5 ммоль/л
Жалобы на головную боль, слабость

Вопрос: Каков предполагаемый диагноз и первоочередные мероприятия?"""

        case_label = ttk.Label(main_frame, text=case_text, justify=tk.LEFT)
        case_label.pack(pady=10, anchor=tk.W)

        # Поле для ответа
        ttk.Label(main_frame, text="Ваш ответ:").pack(anchor=tk.W, pady=(20, 5))
        self.answer_text = tk.Text(main_frame, height=8, width=50)
        self.answer_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Подтвердить",
                   command=lambda: self.check_answer(captcha_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=captcha_window.destroy).pack(side=tk.LEFT, padx=5)

        captcha_window.wait_window()

    def check_answer(self, window):
        """Проверка ответа на медицинскую капчу"""
        answer = self.answer_text.get("1.0", tk.END).lower()

        # Ключевые слова для проверки
        required_keywords = [
            ['гипертензия', 'гипертония'],
            ['сахарный диабет', 'глюкоза', 'гипергликемия'],
            ['антигипертензивные', 'лечение', 'терапия']
        ]

        # Проверяем наличие ключевых слов из каждой группы
        found_groups = 0
        for group in required_keywords:
            if any(keyword in answer for keyword in group):
                found_groups += 1

        if found_groups >= 2:
            self.verified = True
            window.destroy()
        else:
            messagebox.showerror("Ошибка",
                                 "Ответ недостаточно полный. Опишите диагноз и рекомендуемое лечение.")