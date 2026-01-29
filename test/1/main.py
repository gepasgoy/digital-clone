import tkinter as tkn

root = tkn.Tk()
root['bg'] = "#f29595"
root.title("Тетс")
root.geometry('600x600')

fr1 = tkn.Frame(root, bg='red',height=100,width=100)
fr2 = tkn.Frame(root, bg='green',height=100,width=100)
fr1.pack()
fr2.pack()

root.mainloop()