import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import json

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager (REST API Client)")
        self.root.geometry("600x400")
        
        # Конфигурация API
        self.api_base = "http://localhost:8000"
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загружаем задачи при запуске
        self.load_tasks()
    
    def create_widgets(self):
        # Верхняя панель для добавления задач
        frame_top = ttk.Frame(self.root, padding="10")
        frame_top.pack(fill=tk.X)
        
        ttk.Label(frame_top, text="Новая задача:").pack(anchor=tk.W)
        
        self.title_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.title_var, width=50).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(frame_top, text="Добавить", command=self.add_task).pack(side=tk.LEFT)
        ttk.Button(frame_top, text="Обновить список", command=self.load_tasks).pack(side=tk.LEFT, padx=(10, 0))
        
        # Список задач
        frame_list = ttk.Frame(self.root, padding="10")
        frame_list.pack(fill=tk.BOTH, expand=True)
        
        # Treeview для отображения задач
        columns = ("id", "title", "description", "status")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("description", text="Описание")
        self.tree.heading("status", text="Статус")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=200)
        self.tree.column("description", width=250)
        self.tree.column("status", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка удаления
        ttk.Button(self.root, text="Удалить выбранное", command=self.delete_task).pack(pady=10)
    
    def load_tasks(self):
        """Загружает задачи с API в отдельном потоке"""
        def fetch():
            try:
                response = requests.get(f"{self.api_base}/tasks/")
                response.raise_for_status()
                tasks = response.json()
                
                # Очищаем treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Добавляем задачи
                for task in tasks:
                    self.tree.insert("", tk.END, values=(
                        task["id"],
                        task["title"],
                        task["description"],
                        task["status"]
                    ))
                    
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Не удалось подключиться к API серверу.\nЗапустите api_server.py")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")
        
        # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
        thread = threading.Thread(target=fetch)
        thread.daemon = True
        thread.start()
    
    def add_task(self):
        """Добавляет новую задачу через API"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Предупреждение", "Введите заголовок задачи")
            return
        
        def post():
            try:
                task_data = {"title": title, "description": ""}
                response = requests.post(f"{self.api_base}/tasks/", json=task_data)
                response.raise_for_status()
                
                # Очищаем поле и обновляем список
                self.title_var.set("")
                self.load_tasks()
                
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Нет связи с API сервером")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")
        
        thread = threading.Thread(target=post)
        thread.daemon = True
        thread.start()
    
    def delete_task(self):
        """Удаляет выбранную задачу"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите задачу для удаления")
            return
        
        task_id = self.tree.item(selected[0])["values"][0]
        
        def delete():
            try:
                # В реальном API добавили бы endpoint для удаления
                # Пока просто покажем сообщение
                messagebox.showinfo("Удаление", 
                    f"В реальном приложении здесь был бы DELETE запрос\nна {self.api_base}/tasks/{task_id}/")
                # После удаления обновляем список
                self.load_tasks()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")
        
        thread = threading.Thread(target=delete)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()