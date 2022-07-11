from os import listdir
from os.path import *
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

img = None

title = 'MForge 0.0.1'
zoom = 1.0
font = 'microsoft yahei'
size = 10


def log():
    open('MForge.cfg', 'w').write(
        f'# {title}\n'
        f'zoom={zoom}\n'
        f'font={font}\n'
        f'size={size}\n'
    )


class ScrolledText(Text):
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        for m in (vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()).difference(vars(Text).keys()):
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class ScrolledTreeview(Treeview):
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Treeview.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        for m in (vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()).difference(vars(Treeview).keys()):
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class Page:
    def __init__(self, master):
        # pack
        self.frame = Frame(master)
        self.tree = ScrolledTreeview(self.frame, height=114514, show='tree', selectmode='browse')
        self.text = ScrolledText(self.frame, width=1919810, font=(font, size), undo=True)
        self.canvas = Canvas(self.frame, width=114514, height=1919810, cursor='hand2')
        self.tree.pack(side=LEFT, fill=BOTH)
        self.text.pack(side=RIGHT, fill=BOTH)

        # bind
        self.tree.bind('<ButtonRelease-1>', lambda event: self.Open(self.tree.item(self.tree.focus())['values'][0]))

        self.text.bind('<Key>', lambda event: self.text.edit_separator())
        self.text.bind('<Control-MouseWheel>', lambda event: self.resize(size + event.delta / 120))
        self.text.bind('<Control-equal>', lambda event: self.resize(size + 1))
        self.text.bind('<Control-minus>', lambda event: self.resize(size - 1))
        self.text.bind('<Control-0>', lambda event: self.resize(10))
        self.text.bind('<Control-z>', lambda event: self.text.edit_undo())
        self.text.bind('<Control-y>', lambda event: self.text.edit_redo())
        self.text.bind('<Control-s>', lambda event: [
            open(self.tree.item(self.tree.focus())['values'][0], 'w', encoding='utf-8')
                       .write(self.text.get('0.0', END)), messagebox.showinfo(title, 'Save successfully!')
        ])

        self.canvas.bind('<Configure>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0]))
        self.canvas.bind('<Control-MouseWheel>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0],
                                                                         zoom + event.delta / 120 / 5))
        self.canvas.bind('<Control-equal>',
                         lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], zoom + 0.2))
        self.canvas.bind('<Control-minus>',
                         lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], zoom - 0.2))
        self.canvas.bind('<Control-0>', lambda event: self.show(self.tree.item(self.tree.focus())['values'][0], 1))

    def resize(self, new):
        global size
        size = int(new)
        if size <= 0:
            size = 1
        self.text.config(font=(font, size))
        log()

    def show(self, path, new=zoom):
        global img
        global zoom
        zoom = new
        self.canvas.update()
        image = Image.open(path)
        img = ImageTk.PhotoImage(image.resize((int(image.width * zoom), int(image.height * zoom))))
        self.canvas.create_image(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, image=img)
        self.canvas.focus_set()
        log()

    def load(self, Path, parent=''):
        item = self.tree.insert(parent, END, text=basename(Path), values=[Path], open=True)
        for i in listdir(Path):
            path = join(Path, i)
            if isdir(path):
                self.load(path, item)
            else:
                self.tree.insert(item, END, text=i, values=[path], open=True)

    def Open(self, path):
        if path.endswith('.png') or path.endswith('.jpg'):
            self.text.pack_forget()
            self.canvas.pack(side=RIGHT, fill=BOTH)
            self.show(path)
        else:
            self.canvas.pack_forget()
            self.text.delete('1.0', END)
            if isdir(path):
                self.text.pack_forget()
                self.canvas.pack(side=RIGHT, fill=BOTH)
                self.canvas.delete('all')
            else:
                self.text.pack(side=RIGHT, fill=BOTH)
                try:
                    self.text.insert('1.0', open(path, encoding='utf-8').read())
                except UnicodeDecodeError:
                    self.text.insert('1.0', open(path, 'br').read())


def Open(path):
    page = Page(fme)
    page.load(path)
    book.add(page.frame, text=basename(path))


if __name__ == '__main__':

    # config
    if exists('MForge.cfg'):
        for line in open('MForge.cfg').read().split('\n'):
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
    else:
        log()

    # window
    main = Tk()
    main.title(title)
    main.geometry('640x480')

    # widget
    fme = Frame(main)
    book = Notebook(fme)
    fme.pack(padx=10, pady=10)
    book.pack()

    # menu
    mainMenu = Menu(tearoff=False)
    fileMenu = Menu(tearoff=False)
    openMenu = Menu(tearoff=False)
    mainMenu.add_cascade(label='file', menu=fileMenu)
    fileMenu.add_command(label='open', command=lambda: Open(filedialog.askdirectory()))
    main.config(menu=mainMenu)

    # mainloop
    main.mainloop()
