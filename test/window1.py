import tkinter as tk

def open_second_window(root):
    root.destroy()  # закрыть первое окно
    import window2  # импортировать и открыть второе окно (оно само создаст Toplevel)

def main():
    root = tk.Tk()
    root.title("Окно 1")

    label = tk.Label(root, text="Введите пароль:")
    label.pack(pady=10)

    entry = tk.Entry(root, show="*")
    entry.pack()

    def check():
        if entry.get() == "123":  # проверка
            open_second_window(root)

    btn = tk.Button(root, text="Войти", command=check)
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
