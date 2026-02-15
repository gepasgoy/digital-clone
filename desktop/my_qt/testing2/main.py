import sys, random, requests, subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMenu,
    QDialog, QVBoxLayout, QFormLayout, QLabel, QPushButton,
    QMessageBox, QAbstractItemView, QTreeWidget, QTreeWidgetItem, QWidget,QLineEdit, QTableWidget, QComboBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QTimer, QUrl, Qt
from PySide6.QtGui import QColor

API = "http://127.0.0.1:8000"

# ---------------- UI LOADER ----------------
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
        r = requests.post(API+"/login", json={
            "mail": self.ui.mailEdit.text(),
            "password": self.ui.passEdit.text()
        })
        if r.status_code != 200:
            self.ui.statusLabel.setText("login fail")
            return
        token = r.json()["access_token"]
        self.v = Verify(token)
        self.v.show()
        self.close()

# ---------------- VERIFY ----------------
class Verify(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.ui = load_ui("Verify.ui", self)
        self.token = token
        self.sms_ok = False
        self.captcha_ok = False
        self.sms = str(random.randint(1000,9999))
        self.ui.smsLabel.setText(f"SMS код: {self.sms}")
        self.ui.smsBtn.clicked.connect(self.check_sms)
        self.ui.captchaLabel.setText(
            "Пациент 65 лет, АД 170/100, глюкоза 8.5 — диагноз?"
        )
        self.ui.captchaBtn.clicked.connect(self.check_captcha)

    def check_sms(self):
        if self.ui.smsEdit.text() == self.sms:
            self.sms_ok = True
            self.try_open_main()

    def check_captcha(self):
        if "гипер" in self.ui.captchaEdit.text().lower():
            self.captcha_ok = True
            self.try_open_main()

    def try_open_main(self):
        if self.sms_ok and self.captcha_ok:
            me = requests.get(
                API+"/me",
                headers={"Authorization": f"Bearer {self.token}"}
            ).json()
            self.m = Main(self.token, me["role"])
            self.m.show()
            self.close()

# ---------------- HELPERS ----------------
def age_group(age):
    if age >= 60:
        return "Пожилой"
    if age < 18:
        return "Ребёнок"
    return "Взрослый"

def risk_from_age(age):
    if age >= 65:
        return "high"
    if age >= 45:
        return "medium"
    return "low"

# ---------------- MAIN ----------------
class Main(QMainWindow):
    def __init__(self, token, role):
        super().__init__()
        self.ui = load_ui("Main.ui")
        self.setCentralWidget(self.ui)

        self.token = token
        self.role = role
        self.patients_data = []
        self.notifications = []

        # ---------- STREAMLIT ----------
        self.streamlit_process = subprocess.Popen(
            [
                "streamlit",
                "run",
                "dashboard.py",
                "--server.port",
                "8501",
                "--server.headless",
                "true"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        QTimer.singleShot(3000, self.init_webview)

        # ---------- PATIENT TAB ----------
        self.init_patients_tab()
        self.load_patients_from_api()
        self.init_quick_actions()

        # ---------- ДОПОЛНИТЕЛЬНЫЕ ВКЛАДКИ ----------
        self.add_extra_tabs()
        self.add_journal_tab()
        self.add_recommendations_tab()

        # ---------- РОЛЕВОЙ ДОСТУП ----------
        self.setup_role_permissions()

        # ---------- УВЕДОМЛЕНИЯ ----------
        self.setup_notifications()

    # ---------- STREAMLIT VIEW ----------
    def init_webview(self):
        self.web = QWebEngineView(self)
        self.web.setUrl(QUrl("http://localhost:8501/?page=overview"))
        self.ui.dashboardLayout.addWidget(self.web)

    # ---------- НОВЫЕ ВКЛАДКИ ----------
    def add_journal_tab(self):
        self.journal_tab = QWidget()
        layout = QVBoxLayout(self.journal_tab)

        # Кнопка добавления записи
        self.add_journal_btn = QPushButton("Добавить запись")
        self.add_journal_btn.clicked.connect(self.show_add_journal_dialog)
        layout.addWidget(self.add_journal_btn)

        # Таблица журнала
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(4)
        self.journal_table.setHorizontalHeaderLabels(["Дата", "Тип", "Описание", "Пациент"])
        self.journal_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.journal_table)

        self.ui.tabWidget.addTab(self.journal_tab, "Журнал")
        self.load_journal()

    def show_add_journal_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Новая запись в журнал")
        layout = QFormLayout(dialog)

        date_edit = QLineEdit()
        date_edit.setPlaceholderText("ГГГГ-ММ-ДД")
        type_edit = QLineEdit()
        type_edit.setPlaceholderText("Приём / Исследование / ...")
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Описание")
        patient_edit = QLineEdit()
        patient_edit.setPlaceholderText("ФИО пациента")

        layout.addRow("Дата:", date_edit)
        layout.addRow("Тип:", type_edit)
        layout.addRow("Описание:", desc_edit)
        layout.addRow("Пациент:", patient_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            data = {
                "date": date_edit.text(),
                "type": type_edit.text(),
                "description": desc_edit.text(),
                "patient_name": patient_edit.text()
            }
            # Отправка на сервер
            r = requests.post(
                f"{API}/journal",
                json=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if r.status_code == 200:
                new_entry = r.json()
                self.insert_journal_row(new_entry)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить запись")
        
    def insert_journal_row(self, entry):
        row = self.journal_table.rowCount()
        self.journal_table.insertRow(row)
        self.journal_table.setItem(row, 0, QTableWidgetItem(entry["date"]))
        self.journal_table.setItem(row, 1, QTableWidgetItem(entry["type"]))
        self.journal_table.setItem(row, 2, QTableWidgetItem(entry["description"]))
        self.journal_table.setItem(row, 3, QTableWidgetItem(entry["patient_name"]))

    def add_extra_tabs(self):
        # Вкладка Визуализация
        self.vis_tab = QWidget()
        layout = QVBoxLayout(self.vis_tab)
        self.vis_webview = QWebEngineView()
        self.vis_webview.setUrl(QUrl("http://localhost:8501/?page=analytics"))
        layout.addWidget(self.vis_webview)
        self.ui.tabWidget.addTab(self.vis_tab, "Визуализация")

        # Вкладка Документы
        self.doc_tab = QWidget()
        layout = QVBoxLayout(self.doc_tab)
        self.doc_table = QTableWidget()
        self.doc_table.setColumnCount(3)
        self.doc_table.setHorizontalHeaderLabels(["Название", "Дата", "Ссылка"])
        self.doc_table.setRowCount(2)
        self.doc_table.setItem(0, 0, QTableWidgetItem("Выписка"))
        self.doc_table.setItem(0, 1, QTableWidgetItem("2026-02-14"))
        self.doc_table.setItem(0, 2, QTableWidgetItem("Скачать"))
        self.doc_table.setItem(1, 0, QTableWidgetItem("Результаты анализа"))
        self.doc_table.setItem(1, 1, QTableWidgetItem("2026-02-13"))
        self.doc_table.setItem(1, 2, QTableWidgetItem("Скачать"))
        layout.addWidget(self.doc_table)
        self.ui.tabWidget.addTab(self.doc_tab, "Документы")

    def add_journal_tab(self):
        self.journal_tab = QWidget()
        layout = QVBoxLayout(self.journal_tab)
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(4)
        self.journal_table.setHorizontalHeaderLabels(["Дата", "Тип", "Описание", "Пациент"])
        layout.addWidget(self.journal_table)
        self.ui.tabWidget.addTab(self.journal_tab, "Журнал")
        self.load_journal()

    def add_recommendations_tab(self):
        self.rec_tab = QWidget()
        layout = QVBoxLayout(self.rec_tab)
        self.rec_tree = QTreeWidget()
        self.rec_tree.setHeaderLabel("Клинические рекомендации")
        for cat in ["Гипертония", "Диабет", "ИБС"]:
            item = QTreeWidgetItem([cat])
            r = requests.get(f"{API}/recommendations", params={"diagnosis": cat})
            if r.status_code == 200:
                recs = r.json()
                if isinstance(recs, list):
                    for rec in recs:
                        child = QTreeWidgetItem([rec])
                        item.addChild(child)
            self.rec_tree.addTopLevelItem(item)
        layout.addWidget(self.rec_tree)
        self.ui.tabWidget.addTab(self.rec_tab, "Рекомендации")

    def load_journal(self):
        r = requests.get(f"{API}/journal", headers={"Authorization": f"Bearer {self.token}"})
        if r.status_code == 200:
            data = r.json()
            self.journal_table.setRowCount(0)
            for entry in data:
                self.insert_journal_row(entry)

    # ---------- PATIENTS TAB ----------
    def init_patients_tab(self):
        ui = self.ui
        ui.patientsTable.setColumnCount(7)  # добавили колонку для тегов
        ui.patientsTable.setHorizontalHeaderLabels(
            ["ID","ФИО","Диагноз","Отделение","Статус","Возраст","Теги"]
        )

        ui.deptBox.addItems(["Все"])
        ui.statusBox.addItems(["Все"])
        ui.ageBox.addItems(["Все","Ребёнок","Взрослый","Пожилой"])

        # Добавляем фильтр по тегам
        ui.tagBox = QComboBox()
        ui.tagBox.addItems(["Все", "Диабет", "Гипертония", "Беременность", "Сердечно-сосудистые"])
        ui.filterLayout.addWidget(ui.tagBox)
        ui.tagBox.currentTextChanged.connect(self.apply_filters)

        for w in [ui.searchNameEdit, ui.searchIdEdit, ui.searchDiagEdit]:
            w.textChanged.connect(self.apply_filters)

        ui.deptBox.currentTextChanged.connect(self.apply_filters)
        ui.statusBox.currentTextChanged.connect(self.apply_filters)
        ui.ageBox.currentTextChanged.connect(self.apply_filters)

        ui.patientsTable.setContextMenuPolicy(Qt.CustomContextMenu)
        ui.patientsTable.customContextMenuRequested.connect(self.patient_menu)
        ui.patientsTable.setSelectionMode(QAbstractItemView.MultiSelection)  # групповой выбор

    def init_quick_actions(self):
        ui = self.ui
        ui.qaNewTreatmentBtn.clicked.connect(self.qa_new_treatment)
        ui.qaVisitBtn.clicked.connect(self.qa_visit)
        ui.qaResearchBtn.clicked.connect(self.qa_research)
        ui.qaEpicrisisBtn.clicked.connect(self.qa_epicrisis)

        # Кнопка групповых операций
        ui.qaGroupBtn = QPushButton("Групповые операции")
        ui.qaGroupBtn.clicked.connect(self.group_operations)
        ui.quickBox.layout().addWidget(ui.qaGroupBtn)

        # Кнопка уведомлений
        ui.notifBtn = QPushButton("Уведомления (0)")
        ui.notifBtn.clicked.connect(self.show_notification_center)
        ui.quickBox.layout().addWidget(ui.notifBtn)

    def setup_role_permissions(self):
        if self.role != 2:  # не админ
            self.ui.quickBox.setVisible(False)

    # ---------- LOAD FROM API ----------
    def load_patients_from_api(self):
        if self.role != 2:
            return
        r = requests.get(
            API+"/patients",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        if r.status_code != 200:
            return
        data = r.json()["patients"]
        self.patients_data = []
        for p in data:
            self.patients_data.append({
                "id": p["id"],
                "name": f'{p["second_name"]} {p["first_name"]} {p["patronomyc"]}',
                "diag": "—",
                "dept": "—",
                "status": "—",
                "age": p["age"],
                "risk": risk_from_age(p["age"]),
                "tags": p.get("tags", "")
            })
        self.apply_filters()

    # ---------- FILTER ----------
    def apply_filters(self):
        ui = self.ui
        rows = []
        tag_filter = ui.tagBox.currentText()
        for p in self.patients_data:
            if ui.searchNameEdit.text().lower() not in p["name"].lower():
                continue
            if ui.searchIdEdit.text() and ui.searchIdEdit.text() != str(p["id"]):
                continue
            if ui.searchDiagEdit.text().lower() not in p["diag"].lower():
                continue
            ag = age_group(p["age"])
            if ui.ageBox.currentText() != "Все" and ag != ui.ageBox.currentText():
                continue
            if tag_filter != "Все" and tag_filter not in p["tags"]:
                continue
            rows.append(p)
        self.fill_table(rows)

    # ---------- TABLE ----------
    def fill_table(self, data):
        t = self.ui.patientsTable
        t.setRowCount(len(data))
        colors = {
            "high": QColor("#ffb3b3"),
            "medium": QColor("#ffe0b3"),
            "low": QColor("#b3ffcc")
        }
        for r, p in enumerate(data):
            vals = [p["id"], p["name"], p["diag"], p["dept"], p["status"], p["age"], p["tags"]]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setBackground(colors[p["risk"]])
                t.setItem(r, c, item)
        t.resizeColumnsToContents()

    # ---------- CONTEXT MENU ----------
    def patient_menu(self, pos):
        table = self.ui.patientsTable
        row = table.currentRow()
        if row < 0:
            return
        pid = int(table.item(row,0).text())
        menu = QMenu()
        a_hist = menu.addAction("История болезней")
        a_treat = menu.addAction("Назначения")
        a_res = menu.addAction("Исследования")
        menu.addSeparator()
        tags_menu = menu.addMenu("Назначить тег")
        for tag in ["Диабет", "Гипертония", "Беременность", "Сердечно-сосудистые"]:
            action = tags_menu.addAction(tag)
            action.triggered.connect(lambda checked, t=tag: self.assign_tag(pid, t))
        act = menu.exec(table.mapToGlobal(pos))
        if act == a_hist:
            self.open_patient_tab(pid, "history")
        elif act == a_treat:
            self.open_patient_tab(pid, "treat")
        elif act == a_res:
            self.open_patient_tab(pid, "research")

    def assign_tag(self, pid, tag):
        requests.patch(
            f"{API}/patients/{pid}/tags",
            params={"tag": tag},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        for p in self.patients_data:
            if p["id"] == pid:
                p["tags"] = tag
                break
        self.apply_filters()

    # ---------- GROUP OPERATIONS ----------
    def group_operations(self):
        selected_rows = set()
        for item in self.ui.patientsTable.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            QMessageBox.information(self, "Информация", "Не выбрано ни одного пациента")
            return
        patient_ids = [int(self.ui.patientsTable.item(row, 0).text()) for row in selected_rows]
        dialog = QDialog(self)
        dialog.setWindowTitle("Групповые операции")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Выберите тег для назначения:"))
        combo = QComboBox()
        combo.addItems(["Диабет", "Гипертония", "Беременность", "Сердечно-сосудистые"])
        layout.addWidget(combo)
        btn = QPushButton("Применить")
        layout.addWidget(btn)
        btn.clicked.connect(lambda: self.apply_bulk_tag(patient_ids, combo.currentText(), dialog))
        dialog.exec()

    def apply_bulk_tag(self, patient_ids, tag, dialog):
        requests.post(
            f"{API}/patients/bulk/tags",
            json={"patient_ids": patient_ids, "tag": tag},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        for p in self.patients_data:
            if p["id"] in patient_ids:
                p["tags"] = tag
        self.apply_filters()
        dialog.accept()

    # ---------- DRUG INTERACTION (DIALOG) ----------
    def qa_new_treatment(self):
        pid = self.get_selected_patient_id()
        if not pid:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Новое назначение")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Пациент ID: {pid}"))
        form = QFormLayout()
        self.drug1_edit = QLineEdit()
        self.drug2_edit = QLineEdit()
        form.addRow("Препарат 1:", self.drug1_edit)
        form.addRow("Препарат 2:", self.drug2_edit)
        layout.addLayout(form)
        check_btn = QPushButton("Проверить взаимодействие")
        layout.addWidget(check_btn)
        result_label = QLabel("")
        layout.addWidget(result_label)
        check_btn.clicked.connect(lambda: self.check_interaction(result_label))
        save_btn = QPushButton("Сохранить назначение")
        layout.addWidget(save_btn)
        save_btn.clicked.connect(dialog.accept)
        dialog.exec()

    def check_interaction(self, label):
        drug1 = self.drug1_edit.text().strip()
        drug2 = self.drug2_edit.text().strip()
        if not drug1 or not drug2:
            label.setText("Введите оба препарата")
            return
        r = requests.get(f"{API}/drug-interaction", params={"drug1": drug1, "drug2": drug2})
        if r.status_code == 200:
            data = r.json()
            if data["interaction"]:
                label.setText(f"Взаимодействие: {data['interaction']} (severity: {data['severity']})")
            else:
                label.setText("Взаимодействий не найдено")
        else:
            label.setText("Ошибка проверки")

    # ---------- NOTIFICATIONS ----------
    def setup_notifications(self):
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_notifications)
        self.notification_timer.start(30000)  # каждые 30 сек
        self.check_notifications()

    def check_notifications(self):
        r = requests.get(f"{API}/notifications", headers={"Authorization": f"Bearer {self.token}"})
        if r.status_code == 200:
            data = r.json()
            self.notifications = data.get("notifications", [])
            self.ui.notifBtn.setText(f"Уведомления ({len(self.notifications)})")
            for n in self.notifications:
                if n.get("priority") == "high":
                    self.show_notification_popup(n["message"])

    def show_notification_popup(self, message):
        # Простое всплывающее окно
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Критическое уведомление")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.show()

    def show_notification_center(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Центр уведомлений")
        layout = QVBoxLayout(dialog)
        tree = QTreeWidget()
        tree.setHeaderLabel("Уведомления")
        groups = {"high": "Критические", "medium": "Предупреждения", "low": "Информационные"}
        for priority, title in groups.items():
            group_item = QTreeWidgetItem([title])
            for n in self.notifications:
                if n.get("priority") == priority:
                    item = QTreeWidgetItem([n["message"]])
                    group_item.addChild(item)
            tree.addTopLevelItem(group_item)
        layout.addWidget(tree)
        dialog.exec()

    # ---------- FAST ACTIONS (заглушки) ----------
    def get_selected_patient_id(self):
        t = self.ui.patientsTable
        row = t.currentRow()
        if row < 0:
            print("Пациент не выбран")
            return None
        return int(t.item(row,0).text())

    def qa_visit(self):
        pid = self.get_selected_patient_id()
        if not pid: return
        print("прием для", pid)

    def qa_epicrisis(self):
        pid = self.get_selected_patient_id()
        if not pid: return
        print("эпикриз для", pid)

    def qa_research(self):
        pid = self.get_selected_patient_id()
        if not pid: return
        print("исследование добавлено")

    # ---------- OPEN PATIENT TAB (заглушки) ----------
    def open_patient_tab(self, pid, mode):
        r = requests.get(
            API + "/medical-card",
            params={"patient_id": pid},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        if r.status_code != 200:
            print("medical-card error", r.text)
            return
        data = r.json()
        if mode == "research":
            self.fill_research(data["research"])
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_research)
        elif mode == "treat":
            self.fill_treatments([])
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_treatments)
        elif mode == "history":
            self.fill_history([])
            self.ui.tabWidget.setCurrentWidget(self.ui.tab_history)

    def fill_history(self, items):
        t = self.ui.historyTable
        t.setColumnCount(1)
        t.setHorizontalHeaderLabels(["Нет данных"])
        t.setRowCount(0)

    def fill_treatments(self, items):
        t = self.ui.treatmentTable
        t.setColumnCount(1)
        t.setHorizontalHeaderLabels(["Нет данных"])
        t.setRowCount(0)

    def fill_research(self, items):
        t = self.ui.researchTable
        t.setColumnCount(4)
        t.setHorizontalHeaderLabels(["ID","Название","Дата","Результат"])
        t.setRowCount(len(items))
        for r,x in enumerate(items):
            t.setItem(r,0,QTableWidgetItem(str(x["id"])))
            t.setItem(r,1,QTableWidgetItem(x["name"]))
            t.setItem(r,2,QTableWidgetItem(str(x["date"])))
            t.setItem(r,3,QTableWidgetItem(str(x["result"])))
        t.resizeColumnsToContents()

    # ---------- CLOSE ----------
    def closeEvent(self, event):
        if hasattr(self, "streamlit_process"):
            self.streamlit_process.terminate()
        event.accept()

# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if "--test" in sys.argv:
        token = "test_token"
        role = 2
        w = Main(token, role)
    else:
        w = Login()
    w.show()
    app.exec()