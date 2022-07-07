import os
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk

img = None

title = 'MForge 0.0.1'
zoom = 1.0
font = 'microsoft yahei'
size = 10


def log():
    open('MForge.config', 'w').write(f'{title}\n'
                                     f'zoom={zoom}\n'
                                     f'font={font}\n'
                                     f'size={size}\n')


def resize(new):
    global size
    size = int(new)
    if size <= 0:
        size = 1
    text.config(font=(font, size))
    log()


def show(new=zoom):
    global img
    global zoom
    zoom = new
    canvas.update()
    image = Image.open(tree.item(tree.focus())['values'][0])
    img = ImageTk.PhotoImage(image.resize((int(image.width * zoom), int(image.height * zoom))))
    canvas.create_image(canvas.winfo_width() / 2, canvas.winfo_height() / 2, image=img)
    canvas.focus_set()
    log()


def load(Path, parent=''):
    item = tree.insert(parent, END, text=os.path.basename(Path), values=[Path], open=True)
    for i in os.listdir(Path):
        path = os.path.join(Path, i)
        if os.path.isdir(path):
            load(path, item)
        else:
            tree.insert(item, END, text=i, values=[path], open=True)


def Open(path):
    if path.endswith('.png') or path.endswith('.jpg'):
        text.pack_forget()
        canvas.pack(side='left', fill='both')
        show()
    else:
        canvas.pack_forget()
        text.delete('1.0', END)
        if os.path.isdir(path):
            text.pack_forget()
        else:
            text.pack(side='left', fill='both')
            text.insert('1.0', open(path, encoding='utf-8').read())


def config():
    win = Toplevel(main)
    win.geometry('320x240')
    Label(win, text='font size:').pack()
    spn = Spinbox(win, from_=1, to=100, font=(font, size), command=lambda: resize(spn.get()))
    spn.pack()
    main.mainloop()


if __name__ == '__main__':

    # config
    for line in open('MForge.config').read().split('\n'):
        if line != title:
            lst = line.split('=')
            if lst[0] == 'version':
                version = lst[1]
            if lst[0] == 'zoom':
                zoom = float(lst[1])
            elif lst[0] == 'font':
                font = lst[1]
            elif lst[0] == 'size':
                size = int(lst[1])

    # window
    main = Tk()
    main.title(title)
    main.geometry('640x480')

    # widget
    fme = Frame(main)
    tree = Treeview(fme, height=114514, show='tree', selectmode='browse')
    bar = tk.Scrollbar(fme, command=tree.yview)
    buff = Frame(fme, width=2, cursor='sb_h_double_arrow')
    text = scrolledtext.ScrolledText(fme, width=1919810, font=(font, size), undo=True)
    canvas = Canvas(fme, width=114514, height=1919810, cursor='hand2')

    # menu
    menu = Menu()
    file = Menu(tearoff=False)
    edit = Menu(tearoff=False)
    menu.add_cascade(label='file', menu=file)
    menu.add_cascade(label='edit', menu=edit)
    menu.add_command(label='config', command=lambda: config())
    main.config(menu=menu)

    # pack
    fme.pack(padx=10, pady=10, fill='both')
    tree.pack(side='left', fill='both')
    bar.pack(side='left', fill='y')
    buff.pack(side='left', fill='y')
    text.pack(side='left', fill='both')

    # bind
    buff.bind('<B1-Motion>', lambda event: [
        tree.pack_forget(),
        tree.column('#0', width=tree.winfo_width() + event.x),
        tree.pack(side='left', fill='both'),
    ])

    tree.bind('<ButtonRelease-1>', lambda event: Open(tree.item(tree.focus())['values'][0]))

    text.bind('<Key>', lambda event: text.edit_separator())
    text.bind('<Control-MouseWheel>', lambda event: resize(size + event.delta / 120))
    text.bind('<Control-equal>', lambda event: resize(size + 1))
    text.bind('<Control-minus>', lambda event: resize(size - 1))
    text.bind('<Control-0>', lambda event: resize(10))
    text.bind('<Control-z>', lambda event: text.edit_undo())
    text.bind('<Control-y>', lambda event: text.edit_redo())
    text.bind('<Control-s>', lambda event: [
        open(tree.item(tree.focus())['values'][0], 'w').write(text.get('0.0', END)),
        messagebox.showinfo(title, 'Save successfully!')
    ])

    canvas.bind('<Configure>', lambda event: show())
    canvas.bind('<Control-MouseWheel>', lambda event: show(zoom + event.delta / 120 / 5))
    canvas.bind('<Control-equal>', lambda event: show(zoom + 0.2))
    canvas.bind('<Control-minus>', lambda event: show(zoom - 0.2))
    canvas.bind('<Control-0>', lambda event: show(1))

    # init
    load(filedialog.askdirectory())

    # mainloop
    main.mainloop()
