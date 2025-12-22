import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.geometry("335x200")
frame1 = tk.Frame(root,pady=30)
frame1.pack()
frame2 = tk.Frame(root, pady=20)
frame2.pack()

info_label = tk.Label(frame1,text="Для подтверждения входа вам нужно ввести код из смс:")
info_label.pack(expand=True)
test_code_label = tk.Label(frame1,text="Тестовый код: 111111")
test_code_label.pack(expand=True)

label1 = tk.Label(frame2, text="Введите код:", wraplength=200)
main_entry = tk.Entry(frame2)
label1.grid(row=0,column=0)
main_entry.grid(row=0,column=1)

def check_entry():
    code = main_entry.get()
    if code == "111111":
        print("good")
        root.destroy()
    else:
        messagebox.showerror(title="Ошибка",message="Неправильный код!")

btn = tk.Button(root,text="Отправить", command=lambda: check_entry()).pack()


def run():
    root.mainloop()