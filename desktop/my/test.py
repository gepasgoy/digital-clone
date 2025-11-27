import tkinter as tk

root = tk.Tk()
root.title("Три фрейма")
root.geometry("600x400")

# Настройка весов для строк
root.grid_rowconfigure(0, weight=30)
root.grid_rowconfigure(1, weight=50)
root.grid_rowconfigure(2, weight=20)
root.grid_columnconfigure(0, weight=1)

# Создание фреймов
frame1 = tk.Frame(root, bg="red", relief="raised", borderwidth=2)
frame2 = tk.Frame(root, bg="green", relief="raised", borderwidth=2)
frame3 = tk.Frame(root, bg="blue", relief="raised", borderwidth=2)

# Размещение фреймов
frame1.grid(row=0, column=0, sticky="nsew")
frame2.grid(row=1, column=0, sticky="nsew")
frame3.grid(row=2, column=0, sticky="nsew")

root.mainloop()