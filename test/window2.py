import tkinter as tk

def open_second():
    second = tk.Toplevel()
    second.title("Второе окно")
    tk.Label(second, text="Это второе окно").pack(padx=20, pady=20)

def close_first_and_open_second():
    first.destroy()
    open_second()

root = tk.Tk()

first = tk.Toplevel(root)
first.title("Первое окно")

tk.Label(first, text="Это первое окно").pack(padx=20, pady=20)
tk.Button(first, text="Далее", command=close_first_and_open_second).pack()

root.wait_window(first)
