import tkinter as tk
from tkinter import ttk, messagebox
from data.mock_data import MockData
from clinical.interactions import DrugInteractionChecker


class PrescriptionsWidget:
    def __init__(self, parent, audit_logger):
        self.parent = parent
        self.audit_logger = audit_logger
        self.interaction_checker = DrugInteractionChecker()

        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов для назначений"""
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - форма назначения
        left_frame = ttk.LabelFrame(main_frame, text="Создание назначения", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.create_prescription_form(left_frame)

        # Правая панель - текущие назначения
        right_frame = ttk.LabelFrame(main_frame, text="Активные назначения", padding="15")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_prescriptions_list(right_frame)

    def create_prescription_form(self, parent):
        """Создание формы для назначения препаратов"""
        # Выбор пациента
        ttk.Label(parent, text="Пациент:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(parent, textvariable=self.patient_var,
                                     values=[p['name'] for p in MockData.get_patients()],
                                     state="normal", width=25)
        patient_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        patient_combo.bind('<KeyRelease>', self.on_patient_search)

        # Выбор препарата МНН
        ttk.Label(parent, text="Препарат (МНН):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.medication_var = tk.StringVar()
        medication_combo = ttk.Combobox(parent, textvariable=self.medication_var,
                                        values=MockData.get_medications(),
                                        state="readonly", width=25)
        medication_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        medication_combo.bind('<<ComboboxSelected>>', self.on_medication_selected)

        # Дозировка
        ttk.Label(parent, text="Дозировка:").grid(row=2, column=0, sticky=tk.W, pady=5)
        dosage_frame = ttk.Frame(parent)
        dosage_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        self.dosage_var = tk.DoubleVar(value=50.0)
        dosage_spin = ttk.Spinbox(dosage_frame, from_=0.1, to=1000.0, increment=0.1,
                                  textvariable=self.dosage_var, width=8)
        dosage_spin.pack(side=tk.LEFT)

        ttk.Label(dosage_frame, text="мг").pack(side=tk.LEFT, padx=(5, 0))

        # Частота приема
        ttk.Label(parent, text="Частота:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.frequency_var = tk.StringVar(value="2 раза в день")
        frequency_combo = ttk.Combobox(parent, textvariable=self.frequency_var,
                                       values=["1 раз в день", "2 раза в день", "3 раза в день",
                                               "4 раза в день", "по требованию"],
                                       state="readonly", width=25)
        frequency_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Продолжительность
        ttk.Label(parent, text="Продолжительность:").grid(row=4, column=0, sticky=tk.W, pady=5)
        duration_frame = ttk.Frame(parent)
        duration_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        self.duration_var = tk.IntVar(value=7)
        duration_spin = ttk.Spinbox(duration_frame, from_=1, to=365,
                                    textvariable=self.duration_var, width=8)
        duration_spin.pack(side=tk.LEFT)
        ttk.Label(duration_frame, text="дней").pack(side=tk.LEFT, padx=(5, 0))

        # Проверка взаимодействий
        self.interaction_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Проверить лекарственные взаимодействия",
                        variable=self.interaction_var).grid(row=5, column=0, columnspan=2,
                                                            sticky=tk.W, pady=10)

        # Кнопка создания назначения
        ttk.Button(parent, text="Создать назначение",
                   command=self.create_prescription).grid(row=6, column=0, columnspan=2, pady=10)

        # Поле для предупреждений
        self.warning_text = tk.Text(parent, height=4, width=40, state=tk.DISABLED,
                                    background="#FFF3CD", foreground="#856404")
        self.warning_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        parent.columnconfigure(1, weight=1)

    def create_prescriptions_list(self, parent):
        """Создание списка активных назначений"""
        # Панель поиска
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=20)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Таблица назначений
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('Пациент', 'Препарат', 'Дозировка', 'Статус', 'Дата начала')
        self.prescriptions_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.prescriptions_tree.heading(col, text=col)
            self.prescriptions_tree.column(col, width=100)

        self.prescriptions_tree.column('Пациент', width=150)
        self.prescriptions_tree.column('Препарат', width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.prescriptions_tree.yview)
        self.prescriptions_tree.configure(yscrollcommand=scrollbar.set)

        self.prescriptions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Заполняем тестовыми данными
        self.load_sample_prescriptions()

    def on_patient_search(self, event):
        """Обработка поиска пациента"""
        pass

    def on_medication_selected(self, event):
        """Обработка выбора препарата"""
        medication = self.medication_var.get()
        self.show_medication_warnings(medication)

    def show_medication_warnings(self, medication):
        """Показать предупреждения для препарата"""
        self.warning_text.config(state=tk.NORMAL)
        self.warning_text.delete(1.0, tk.END)

        warnings = {
            "Метформин": "Противопоказан при почечной недостаточности. Контроль функции почек.",
            "Варфарин": "Требуется регулярный контроль МНО. Множественные лекарственные взаимодействия.",
            "Эналаприл": "Контроль АД, функции почек, калия крови. Противопоказан при беременности.",
            "Аторвастатин": "Контроль печеночных ферментов. Противопоказан при активных заболеваниях печени."
        }

        if medication in warnings:
            self.warning_text.insert(1.0, f"⚠️ {warnings[medication]}")

        self.warning_text.config(state=tk.DISABLED)

    def create_prescription(self):
        """Создание нового назначения"""
        patient = self.patient_var.get()
        medication = self.medication_var.get()
        dosage = self.dosage_var.get()

        if not patient or not medication:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return

        # Проверка допустимой дозировки
        if not self.check_dosage(medication, dosage):
            return

        # Проверка взаимодействий
        if self.interaction_var.get():
            interactions = self.interaction_checker.check_interactions([medication])
            if interactions:
                messagebox.showwarning("Взаимодействия",
                                       f"Обнаружены потенциальные взаимодействия: {', '.join(interactions)}")

        # Создание назначения
        self.audit_logger.log("CREATE_PRESCRIPTION",
                              f"Created prescription: {medication} {dosage}mg for {patient}")

        messagebox.showinfo("Успех", "Назначение успешно создано")
        self.clear_form()

    def check_dosage(self, medication, dosage):
        """Проверка допустимой дозировки"""
        max_dosages = {
            "Метформин": 3000,
            "Эналаприл": 40,
            "Аторвастатин": 80,
            "Амлодипин": 10,
            "Бисопролол": 20
        }

        if medication in max_dosages and dosage > max_dosages[medication]:
            messagebox.showerror("Ошибка дозировки",
                                 f"Максимальная дозировка для {medication}: {max_dosages[medication]} мг")
            return False
        return True

    def clear_form(self):
        """Очистка формы"""
        self.medication_var.set('')
        self.dosage_var.set(50.0)
        self.frequency_var.set('2 раза в день')
        self.duration_var.set(7)
        self.warning_text.config(state=tk.NORMAL)
        self.warning_text.delete(1.0, tk.END)
        self.warning_text.config(state=tk.DISABLED)

    def load_sample_prescriptions(self):
        """Загрузка тестовых назначений"""
        sample_data = [
            ("Иванов И.И.", "Метформин", "1000 мг", "Активно", "01.12.2023"),
            ("Петрова М.С.", "Эналаприл", "10 мг", "Активно", "15.12.2023"),
            ("Сидоров А.П.", "Аторвастатин", "20 мг", "Завершено", "10.11.2023"),
            ("Иванов И.И.", "Амлодипин", "5 мг", "Активно", "01.12.2023")
        ]

        for item in sample_data:
            self.prescriptions_tree.insert('', 'end', values=item)