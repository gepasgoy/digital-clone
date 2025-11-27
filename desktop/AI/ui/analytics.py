import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime, timedelta


class AnalyticsWidget:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов аналитики"""
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка эффективности лечения
        efficacy_frame = ttk.Frame(notebook)
        self.create_efficacy_tab(efficacy_frame)
        notebook.add(efficacy_frame, text="Эффективность лечения")

        # Вкладка статистики
        stats_frame = ttk.Frame(notebook)
        self.create_stats_tab(stats_frame)
        notebook.add(stats_frame, text="Статистика заболеваний")

        # Вкладка рабочей нагрузки
        workload_frame = ttk.Frame(notebook)
        self.create_workload_tab(workload_frame)
        notebook.add(workload_frame, text="Рабочая нагрузка")

    def create_efficacy_tab(self, parent):
        """Создание вкладки эффективности лечения"""
        # Заглушка для виджета эффективности
        placeholder = ttk.Label(parent, text="Виджет 'Эффективность лечения'\n\n"
                                             "• Динамика показателей пациентов\n"
                                             "• Графики улучшения состояния\n"
                                             "• Сравнительный анализ лечения\n"
                                             "• Показатели эффективности терапии",
                                justify=tk.CENTER)
        placeholder.pack(expand=True, pady=50)

    def create_stats_tab(self, parent):
        """Создание вкладки статистики заболеваний"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Статистика по нозологиям
        stats_data = [
            ("Гипертоническая болезнь", 45, "35%"),
            ("Сахарный диабет 2 типа", 28, "22%"),
            ("ОРВИ", 15, "12%"),
            ("ИБС", 12, "9%"),
            ("Остеохондроз", 8, "6%"),
            ("Прочие", 20, "16%")
        ]

        # Таблица статистики
        tree = ttk.Treeview(main_frame, columns=('Заболевание', 'Количество', 'Процент'),
                            show='headings', height=10)

        tree.heading('Заболевание', text='Заболевание')
        tree.heading('Количество', text='Количество')
        tree.heading('Процент', text='Процент')

        tree.column('Заболевание', width=200)
        tree.column('Количество', width=100)
        tree.column('Процент', width=80)

        for item in stats_data:
            tree.insert('', 'end', values=item)

        tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка обновления
        ttk.Button(main_frame, text="Обновить статистику",
                   command=self.update_stats).pack(pady=10)

    def create_workload_tab(self, parent):
        """Создание вкладки рабочей нагрузки"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Анализ приемов
        workload_data = [
            ("Понедельник", 18, "8:00-16:00"),
            ("Вторник", 22, "8:00-17:00"),
            ("Среда", 15, "8:00-15:00"),
            ("Четверг", 20, "8:00-16:30"),
            ("Пятница", 16, "8:00-15:30"),
            ("Суббота", 8, "9:00-13:00"),
            ("Воскресенье", 2, "дежурство")
        ]

        # Таблица нагрузки
        tree = ttk.Treeview(main_frame, columns=('День', 'Кол-во приемов', 'Рабочее время'),
                            show='headings', height=10)

        tree.heading('День', text='День')
        tree.heading('Кол-во приемов', text='Кол-во приемов')
        tree.heading('Рабочее время', text='Рабочее время')

        tree.column('День', width=120)
        tree.column('Кол-во приемов', width=120)
        tree.column('Рабочее время', width=120)

        for item in workload_data:
            tree.insert('', 'end', values=item)

        tree.pack(fill=tk.BOTH, expand=True)

        # Статистика за неделю
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)

        total_patients = sum(item[1] for item in workload_data)
        avg_per_day = total_patients / len(workload_data)

        ttk.Label(stats_frame, text=f"Всего пациентов за неделю: {total_patients}").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Среднее в день: {avg_per_day:.1f}").pack(anchor=tk.W)

    def update_stats(self):
        """Обновление статистики"""
        # Заглушка для обновления статистики
        print("Статистика обновлена")