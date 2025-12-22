import tkinter as tk
from tkinter import ttk
from ui.patient_list import PatientList
from ui.prescriptions import PrescriptionsWidget
from ui.analytics import AnalyticsWidget


class MainWindow:
    def __init__(self, parent, user_id, user_role, audit_logger, inactivity_timer):
        self.parent = parent
        self.user_id = user_id
        self.user_role = user_role
        self.audit_logger = audit_logger
        self.inactivity_timer = inactivity_timer

        self.frame = None
        self.notebook = None

    def show(self):
        """Показать главное окно"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.create_menu()
        self.create_notebook()
        self.create_status_bar()

        self.audit_logger.log("APP_OPEN", f"User {self.user_id} opened main application")

    def hide(self):
        """Скрыть главное окно"""
        if self.frame:
            self.frame.destroy()

    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.logout)

        # Меню Пациенты
        patient_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Пациенты", menu=patient_menu)
        patient_menu.add_command(label="Список пациентов",
                                 command=lambda: self.notebook.select(0))
        patient_menu.add_command(label="Новый пациент", command=self.new_patient)

        # Меню Клиника
        clinical_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Клиника", menu=clinical_menu)
        clinical_menu.add_command(label="Назначения",
                                  command=lambda: self.notebook.select(1))

        # Меню Аналитика
        analytics_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Аналитика", menu=analytics_menu)
        analytics_menu.add_command(label="Статистика",
                                   command=lambda: self.notebook.select(2))

    def create_notebook(self):
        """Создание вкладок приложения"""
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка списка пациентов
        self.patient_list = PatientList(self.notebook, self.user_id, self.audit_logger)
        self.notebook.add(self.patient_list.frame, text="Список пациентов")

        # Вкладка назначений
        self.prescriptions = PrescriptionsWidget(self.notebook, self.audit_logger)
        self.notebook.add(self.prescriptions.frame, text="Назначения")

        # Вкладка аналитики
        self.analytics = AnalyticsWidget(self.notebook)
        self.notebook.add(self.analytics.frame, text="Аналитика")

    def create_status_bar(self):
        """Создание строки состояния"""
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        user_info = f"Пользователь: {self.user_id} | Роль: {self.user_role}"
        ttk.Label(status_frame, text=user_info).pack(side=tk.LEFT, padx=5)

        # Таймер неактивности
        self.inactivity_label = ttk.Label(status_frame, text="Неактивность: 0 сек")
        self.inactivity_label.pack(side=tk.RIGHT, padx=5)

        self.update_inactivity_display()

    def update_inactivity_display(self):
        """Обновление отображения времени неактивности"""
        if hasattr(self, 'inactivity_label'):
            inactivity_sec = self.inactivity_timer.get_remaining_time() // 1000
            self.inactivity_label.config(text=f"Неактивность: {inactivity_sec} сек")
            self.parent.after(1000, self.update_inactivity_display)

    def new_patient(self):
        """Создание нового пациента"""
        self.audit_logger.log("NEW_PATIENT", f"User {self.user_id} started creating new patient")
        # Здесь будет логика создания нового пациента

    def logout(self):
        """Выход из системы"""
        self.audit_logger.log("LOGOUT", f"User {self.user_id} initiated logout")
        self.parent.quit()