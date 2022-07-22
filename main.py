from os import listdir
from os.path import *
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from PIL import Image, ImageTk

img = None
tabs = []

title = 'MForge 0.0.1'
zoom = 1.0
font = 'microsoft yahei'
size = 10


class ScrolledText(Text):
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)
        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, )
        self.vbar['command'] = self.yview
        for m in (vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()).difference(vars(Text).keys()):
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))


class ScrolledTreeview(Treeview):
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)
        kw.update({'yscrollcommand': self.vbar.set})
        Treeview.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, )
        self.vbar['command'] = self.yview
        for m in (vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()).difference(vars(Treeview).keys()):
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))


class Page:
    def __init__(self, master, path):
        self.frame = Frame(master)
        self.tree = ScrolledTreeview(self.frame, height=114514, show='tree', selectmode='browse')
        self.text = ScrolledText(self.frame, width=114514, height=1919810, font=(font, size), undo=True)
        self.canvas = Canvas(self.frame, width=114514, height=1919810, cursor='hand2')
        self.text.bind('<Key>', lambda event: self.text.edit_separator())
        self.text.bind('<Control-MouseWheel>', lambda event: self.resize(size + event.delta / 120))
        self.text.bind('<Control-equal>', lambda event: self.resize(size + 1))
        self.text.bind('<Control-minus>', lambda event: self.resize(size - 1))
        self.text.bind('<Control-0>', lambda event: self.resize(10))
        self.text.bind('<Control-z>', lambda event: self.text.edit_undo())
        self.text.bind('<Control-y>', lambda event: self.text.edit_redo())
        if isdir(path):
            self.tree.bind('<ButtonRelease-1>', lambda event: self.Open(self.tree.item(self.tree.focus())['values'][0]))
            self.text.bind('<Control-s>', lambda event: [open(self.tree.item(self.tree.focus())['values'][0], 'w', encoding='utf-8').write(self.text.get('0.0', END)), showinfo(title, 'Save successfully!')])
            self.canvas.bind('<Configure>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0]))
            self.canvas.bind('<Control-MouseWheel>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], zoom + event.delta / 120 / 5))
            self.canvas.bind('<Control-equal>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], zoom + 0.2))
            self.canvas.bind('<Control-minus>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], zoom - 0.2))
            self.canvas.bind('<Control-0>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], 1))
            self.tree.pack(side=LEFT)
            self.load(path)
        else:
            self.text.bind('<Control-s>', lambda event: [open(path, 'w', encoding='utf-8').write(self.text.get('0.0', END)), showinfo(title, 'Save successfully!')])
            self.canvas.bind('<Configure>', lambda event: self.show(path))
            self.canvas.bind('<Control-MouseWheel>', lambda event: self.show(path, zoom + event.delta / 120 / 5))
            self.canvas.bind('<Control-equal>', lambda event: self.show(path, zoom + 0.2))
            self.canvas.bind('<Control-minus>', lambda event: self.show(path, zoom - 0.2))
            self.canvas.bind('<Control-0>', lambda event: self.show(path, 1))
            self.Open(path)
        self.text.pack(side=RIGHT)

    def resize(self, new):
        global size
        size = abs(int(new))
        self.text.config(font=(font, size))

    def show(self, path, new=zoom):
        global img
        global zoom
        zoom = new
        self.canvas.update()
        image = Image.open(path)
        img = ImageTk.PhotoImage(image.resize((int(image.width * zoom), int(image.height * zoom))))
        self.canvas.create_image(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, image=img)
        self.canvas.focus_set()

    def load(self, Path, parent=''):
        item = self.tree.insert(parent, END, text=basename(Path), values=[Path], open=True)
        for i in listdir(Path):
            path = join(Path, i)
            if isdir(path):
                self.load(path, item)
            else:
                self.tree.insert(item, END, text=i, values=[path], open=True)

    def Open(self, path):
        if path.endswith('.png') or path.endswith('.jpg') or isdir(path):
            self.text.pack_forget()
            self.canvas.pack(side=RIGHT)
            self.show(path)
        else:
            self.canvas.pack_forget()
            self.text.delete('1.0', END)
            self.text.pack(side=RIGHT)
            try:
                self.text.insert('1.0', open(path, encoding='utf-8').read())
            except UnicodeDecodeError:
                self.text.insert('1.0', open(path, 'br').read())
            finally:
                self.text.edit_reset()


def Open(paths):
    for path in paths:
        if path in tabs:
            showerror(title, "You have ALREADY opened another one!")
        else:
            book.add(Page(main, path).frame, text=basename(path))
            tabs.append(path)


def test():
    print('hello, world')


if __name__ == '__main__':
    main = Tk()
    main.title(title)
    main.geometry('640x480')
    book = Notebook(main)
    book.enable_traversal()
    book.pack(padx=10, pady=10)
    mainMenu = Menu(tearoff=False)
    fileMenu = Menu(tearoff=False)
    openMenu = Menu(tearoff=False)
    mainMenu.add_cascade(label='file', menu=fileMenu)
    fileMenu.add_cascade(label='open', menu=openMenu)
    openMenu.add_command(label='directory', command=lambda: Open([askdirectory()]))
    openMenu.add_command(label='files', command=lambda: Open(askopenfilenames()))
    mainMenu.add_command(label='test', command=test)
    main.config(menu=mainMenu)
    main.mainloop()
