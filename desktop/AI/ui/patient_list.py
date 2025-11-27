import tkinter as tk
from tkinter import ttk, messagebox
from data.mock_data import MockData


class PatientList:
    def __init__(self, parent, user_id, audit_logger):
        self.parent = parent
        self.user_id = user_id
        self.audit_logger = audit_logger

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_patients()

    def create_widgets(self):
        """Создание виджетов списка пациентов"""
        # Панель поиска и фильтров
        search_frame = ttk.LabelFrame(self.frame, text="Поиск и фильтры", padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Строка поиска
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X, pady=5)

        ttk.Label(search_row, text="Поиск:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.apply_filters)

        # Фильтры
        filters_row = ttk.Frame(search_frame)
        filters_row.pack(fill=tk.X, pady=5)

        ttk.Label(filters_row, text="Отделение:").pack(side=tk.LEFT, padx=(0, 5))
        self.department_var = tk.StringVar(value="Все отделения")
        department_combo = ttk.Combobox(filters_row, textvariable=self.department_var,
                                        values=["Все отделения", "Кардиология", "Неврология", "Терапия", "Хирургия",
                                                "Эндокринология"],
                                        state="readonly", width=15)
        department_combo.pack(side=tk.LEFT, padx=(0, 15))
        department_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        ttk.Label(filters_row, text="Статус:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="Все статусы")
        status_combo = ttk.Combobox(filters_row, textvariable=self.status_var,
                                    values=["Все статусы", "Стабилен", "Тяжелый", "Критический"],
                                    state="readonly", width=12)
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        status_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        ttk.Label(filters_row, text="Возраст:").pack(side=tk.LEFT, padx=(0, 5))
        self.age_var = tk.StringVar(value="Все возраста")
        age_combo = ttk.Combobox(filters_row, textvariable=self.age_var,
                                 values=["Все возраста", "Дети (0-17)", "Взрослые (18-64)", "Пожилые (65+)"],
                                 state="readonly", width=15)
        age_combo.pack(side=tk.LEFT)
        age_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        # Кнопки действий
        actions_frame = ttk.Frame(self.frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(actions_frame, text="Новый пациент",
                   command=self.new_patient).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Обновить",
                   command=self.load_patients).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Экспорт",
                   command=self.export_data).pack(side=tk.LEFT)

        # Таблица пациентов
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем Treeview с полосой прокрутки
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(table_frame,
                                 columns=('ID', 'ФИО', 'Возраст', 'Диагноз', 'Отделение', 'Статус', 'Приоритет'),
                                 show='headings', yscrollcommand=scrollbar.set)

        # Настройка колонок
        columns = {
            'ID': 80, 'ФИО': 200, 'Возраст': 80, 'Диагноз': 150,
            'Отделение': 120, 'Статус': 100, 'Приоритет': 100
        }

        for col, width in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Привязываем двойной клик
        self.tree.bind('<Double-1>', self.on_patient_double_click)

        # Контекстное меню
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Открыть карту", command=self.open_patient_card)
        self.context_menu.add_command(label="Создать назначение", command=self.create_prescription)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить", command=self.delete_patient)

        self.tree.bind('<Button-3>', self.show_context_menu)

    def load_patients(self):
        """Загрузка пациентов в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        patients = MockData.get_patients()

        for patient in patients:
            item = self.tree.insert('', 'end', values=(
                patient['id'],
                patient['name'],
                patient['age'],
                patient['diagnosis'],
                patient['department'],
                patient['status'],
                patient['priority']
            ))

            # Цветовая маркировка по приоритету
            if patient['priority'] == 'Высокий':
                self.tree.set(item, 'Приоритет', '🔴 Высокий')
            elif patient['priority'] == 'Средний':
                self.tree.set(item, 'Приоритет', '🟡 Средний')
            else:
                self.tree.set(item, 'Приоритет', '🟢 Низкий')

    def apply_filters(self, event=None):
        """Применение фильтров к списку пациентов"""
        search_text = self.search_var.get().lower()
        department_filter = self.department_var.get()
        status_filter = self.status_var.get()
        age_filter = self.age_var.get()

        # Сначала показываем всех пациентов
        for item in self.tree.get_children():
            self.tree.item(item, tags=())

        # Применяем фильтры
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            show_item = True

            # Поиск по тексту
            if search_text:
                if not any(search_text in str(value).lower() for value in values):
                    show_item = False

            # Фильтр по отделению
            if department_filter != "Все отделения" and values[4] != department_filter:
                show_item = False

            # Фильтр по статусу
            if status_filter != "Все статусы" and values[5] != status_filter:
                show_item = False

            # Фильтр по возрасту
            if age_filter != "Все возраста":
                age = values[2]
                if age_filter == "Дети (0-17)" and age > 17:
                    show_item = False
                elif age_filter == "Взрослые (18-64)" and (age < 18 or age > 64):
                    show_item = False
                elif age_filter == "Пожилые (65+)" and age < 65:
                    show_item = False

            if not show_item:
                self.tree.detach(item)

    def on_patient_double_click(self, event):
        """Обработка двойного клика по пациенту"""
        self.open_patient_card()

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_patient_card(self):
        """Открыть карту пациента"""
        selection = self.tree.selection()
        if selection:
            patient_id = self.tree.item(selection[0])['values'][0]
            self.audit_logger.log("OPEN_PATIENT_CARD", f"User opened patient {patient_id}")
            messagebox.showinfo("Карта пациента", f"Открыта карта пациента {patient_id}")

    def create_prescription(self):
        """Создать назначение для выбранного пациента"""
        selection = self.tree.selection()
        if selection:
            patient_id = self.tree.item(selection[0])['values'][0]
            patient_name = self.tree.item(selection[0])['values'][1]
            self.audit_logger.log("CREATE_PRESCRIPTION", f"User started prescription for {patient_id}")
            messagebox.showinfo("Назначение", f"Создание назначения для {patient_name}")

    def delete_patient(self):
        """Удалить выбранного пациента"""
        selection = self.tree.selection()
        if selection:
            patient_id = self.tree.item(selection[0])['values'][0]
            patient_name = self.tree.item(selection[0])['values'][1]

            if messagebox.askyesno("Подтверждение", f"Удалить пациента {patient_name}?"):
                self.audit_logger.log("DELETE_PATIENT", f"User deleted patient {patient_id}")
                self.tree.delete(selection[0])

    def new_patient(self):
        """Создать нового пациента"""
        self.audit_logger.log("NEW_PATIENT", "User started creating new patient")
        self.show_patient_form()

    def show_patient_form(self):
        """Показать форму нового пациента"""
        form_window = tk.Toplevel(self.frame)
        form_window.title("Новый пациент")
        form_window.geometry("400x500")

        form_frame = ttk.Frame(form_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Поля формы
        ttk.Label(form_frame, text="ФИО:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(form_frame, text="Возраст:").grid(row=1, column=0, sticky=tk.W, pady=5)
        age_spin = ttk.Spinbox(form_frame, from_=0, to=150, width=28)
        age_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(form_frame, text="Диагноз:").grid(row=2, column=0, sticky=tk.W, pady=5)
        diagnosis_entry = ttk.Entry(form_frame, width=30)
        diagnosis_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(form_frame, text="Отделение:").grid(row=3, column=0, sticky=tk.W, pady=5)
        department_combo = ttk.Combobox(form_frame,
                                        values=["Кардиология", "Неврология", "Терапия", "Хирургия", "Эндокринология"])
        department_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить",
                   command=lambda: self.save_patient(form_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена",
                   command=form_window.destroy).pack(side=tk.LEFT, padx=5)

        form_frame.columnconfigure(1, weight=1)

    def save_patient(self, window):
        """Сохранить нового пациента"""
        self.audit_logger.log("SAVE_PATIENT", "User saved new patient")
        messagebox.showinfo("Успех", "Пациент успешно сохранен")
        window.destroy()
        self.load_patients()

    def export_data(self):
        """Экспорт данных пациентов"""
        self.audit_logger.log("EXPORT_DATA", "User exported patient data")
        messagebox.showinfo("Экспорт", "Данные пациентов экспортированы")