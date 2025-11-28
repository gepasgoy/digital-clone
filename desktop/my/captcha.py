import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.geometry("440x560")
# root.resizable(False,False)
root.title("Мед.Капча")

frame1 = tk.Frame(root)
label_frame = tk.Frame(frame1)
description_label1 = tk.Label(label_frame,text="Пациент: 65 лет")
description_label2 = tk.Label(label_frame,text="АД: 170/100")
description_label3 = tk.Label(label_frame,text="Глюкоза: 8.5 ммоль/л")
description_label1.pack()
description_label2.pack()
description_label3.pack()

label_frame.pack(expand= True)

frame1.place(rely=0,relwidth=1,relheight=0.3)

frame2 = tk.Frame(root)
label2 = tk.Label(frame2,text="Для прохождения капчи, вам нужно поставить диагноз и назначить терапию по показателям выше.", wraplength=300)
label2.pack(expand=True)
answer_text = tk.Text(frame2,height=10, width=50)
answer_text.pack(expand=True,pady=30)

frame2.place(rely=0.3,relwidth=1,relheight=0.7)

buttons = tk.Frame(frame2)
buttons.pack(pady=10)


def check_answer():
    """Проверка ответа на медицинскую капчу"""
    answer = answer_text.get("1.0", tk.END).lower()

    # Ключевые слова для проверки
    required_keywords = [
        ['гипертензия', 'гипертония'],
        ['сахарный диабет', 'глюкоза', 'гипергликемия'],
        ['антигипертензивные', 'лечение', 'терапия']
    ]

    # Проверяем наличие ключевых слов из каждой группы
    found_groups = 0
    for group in required_keywords:
        if any(keyword in answer for keyword in group):
            found_groups += 1

    if found_groups >= 2:
        root.destroy()


    else:
        messagebox.showerror("Ошибка",
                             "Ответ недостаточно полный. Опишите диагноз и рекомендуемое лечение.")

tk.Button(buttons, text="Подтвердить",
                   command=lambda: check_answer()).pack(side=tk.LEFT, padx=5)
tk.Button(buttons, text="Отмена",
                   command=root.destroy).pack(side=tk.LEFT, padx=5)

def run():
    root.mainloop()

