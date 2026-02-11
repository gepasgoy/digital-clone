import tkinter as tk
root = tk.Tk()
root.title("Двойник пациента")
root.geometry("900x700")

main_menu = tk.Menu(root)
main_menu.add_cascade(label="Обзор")
main_menu.add_cascade(label="История болезней")
main_menu.add_cascade(label="Назначения")
main_menu.add_cascade(label="Исследования")
main_menu.add_cascade(label="Визуализация")
main_menu.add_cascade(label="Документы")
root.config(menu=main_menu)

root.mainloop()