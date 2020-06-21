#!/usr/bin/env python3
# coding: utf-8

# import Tkinter as tk
# from pdb import set_trace
import argparse
from teimxml import do_main as do_main1
from teimlineword import do_main as do_main2
from teimxmllint import do_main as do_main3
import os
import json

"""
try:
    import Tkinter as tk
    import tkFileDialog as fd
except ImportError:
    import tkinter as tk
    import tkinter.filedialog as fd
    from tkinter import END
    # import tkinter.messagebox as tkMessageBox
    # import tkinter.ttk as ttk
    # from tkinter.filedialog import askopenfile
    from tkinter.font import Font
"""

import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog as fd

from tkinter import END

# import tkinter.messagebox as tkMessageBox
# from tkinter.filedialog import askopenfile

# from tkinter import *

__date__ = "12-03-2019"
__version__ = "0.4.1"
__author__ = "Marta Materni"


class TeimEdit(object):

    def __init__(self, path_tags=None, path_file=None, path_cnf=None):
        self.read_start = (path_file is not None)
        self.path_tags = None
        self.set_path_tags(path_tags)
        #
        self.path_file0 = None
        self.path_file1 = None
        self.path_file2 = None
        self.path_file3 = None
        self.set_paths(path_file)
        #
        self.idman = 'k'
        self.parse_cnf(path_cnf)
        #
        self.win = None
        self.text = None
        self.win1 = None
        self.text1 = None
        self.win2 = None
        self.text2 = None

    def set_abs_path(self, bname):
        pwd = os.path.abspath("")
        abs_path = os.path.join(pwd, bname)
        return abs_path

    def set_path_tags(self, path_tags):
        if path_tags is None:
            path_tags = self.set_abs_path('TEIMTAGS.csv')
        self.path_tags = self.set_abs_path(path_tags)
        print(self.path_tags)

    def set_paths(self, path_file0):
        # set_trace()
        if path_file0 is None:
            path_file0 = self.set_abs_path('TEIM0.txt')
        self.path_file0 = self.set_abs_path(path_file0)
        print(self.path_file0)
        self.path_file1 = self.path_file0.replace('.txt', '1.txt')
        print(self.path_file1)
        self.path_file2 = self.path_file0.replace('.txt', '2.xml')
        print(self.path_file2)
        self.path_file3 = self.path_file0.replace('.txt', '3.xml')
        print(self.path_file3)

    def parse_cnf(self, path_cnf):
        if path_cnf is not None:
            with open(path_cnf, "r") as f:
                txt = f.read()
            js = json.loads(txt)
            id = js['idman']
            self.idman = id

    def open(self):
        self.win = tk.Tk()
        self.show_title()
        general_font = ('Arial', 12, 'bold')
        self.win.option_add('*Font', general_font)
        self.win.rowconfigure(0, weight=1)
        self.win.columnconfigure(0, weight=1)
        w = 900
        h = 500
        # ws = self.win.winfo_screenwidth()
        # hs = self.win.winfo_screenheight()
        # x = (ws / 2) - (w / 2)
        # y = (hs / 2) - (h / 2)
        x = 10
        y = 10
        self.win.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.win.protocol("WM_DELETE_WINDOW", self.quit)

        self.text = tk.Text(self.win)
        self.text.grid(sticky='nsew')
        editorFont = ('Serif', 14, 'normal')
        # editorFont = Font(family="Arial", size=12)
        self.text.configure(font=editorFont)

        mb = tk.Menu(self.win)
        self.win.config(menu=mb)
        """
        fm = tk.Menu(mb)
        fm.add_command(label='Open...', command=self.open_file)
        fm.add_command(label='Save', command=self.save_file)
        fm.add_command(label='Save As...', command=self.save_file_as)
        fm.add_separator()
        fm.add_command(label='Quit', command=self.quit)
        mb.add_cascade(label='File', menu=fm)
        mb.add_command(label='Tags', command=self.open_tags)
        # mb.add_cascade(label='Tags', menu=fm2)
        mb.add_command(label='Del', command=self.delete_text)
        mb.add_command(label='Del Entity', command=self.delete_text1)
        mb.add_command(label='Del XML', command=self.delete_text2)
        mb.add_command(label='Elab.Entity', command=self.teimxml)
        mb.add_command(label='Elab.XML', command=self.teimlw)
        """
        fm = tk.Menu(mb)

        fm.add_command(label='Open...', command=self.open_file)
        fm.add_command(label='Save', command=self.save_file)
        fm.add_command(label='Save As...', command=self.save_file_as)
        fm.add_separator()
        fm.add_command(label='Tags', command=self.open_tags)
        fm.add_separator()
        fm.add_command(label='Conf', command=self.open_conf)
        fm.add_separator()
        fm.add_command(label='Del All', command=self.delete_text)
        fm.add_command(label='Del Entity', command=self.delete_text1)
        fm.add_command(label='Del XML', command=self.delete_text2)
        fm.add_separator()
        fm.add_command(label='Elab.Entity', command=self.teimxml)
        fm.add_command(label='Elab. XML', command=self.teimlw)
        fm.add_separator()
        fm.add_command(label='Exit', command=self.quit)
        mb.add_cascade(label='TeiMed', menu=fm)
        mb.add_separator()
        mb.add_separator()

        mb.add_command(label='Tags', command=self.open_tags)
        mb.add_separator()
        mb.add_command(label='Conf', command=self.open_conf)
        mb.add_separator()
        mb.add_command(label='Del ', command=self.delete_text)
        mb.add_command(label='Del Entity', command=self.delete_text1)
        mb.add_command(label='Del XML', command=self.delete_text2)
        mb.add_separator()
        mb.add_command(label='Elab.Entity', command=self.teimxml)
        mb.add_command(label='Elab.XML', command=self.teimlw)

        self.show_text1("")
        self.show_text2("")
        if self.read_start:
            self.read_file0()
        tk.mainloop()

    #########################
    # TEI

    def show_title(self):
        filename = os.path.basename(self.path_file0)
        tagsname = os.path.basename(self.path_tags)
        title = "text:%s   tags:%s  (%s)" % (filename, tagsname, self.idman)
        self.win.title(title)

    def teimxml(self):
        s = self.get_text0()
        with open(self.path_file0, 'w') as f:
            f.write(s)
        os.chmod(self.path_file0, 0o666)
        do_main1(self.path_file0, self.path_tags, self.path_file1)
        with open(self.path_file1, 'rt') as f:
            s = f.read()
        self.show_text1(s)

    def teimlw(self):
        do_main2(self.path_file1, self.path_file2, self.idman)
        do_main3(self.path_file2, self.path_file3)
        with open(self.path_file3, 'rt') as f:
            s = f.read()
        self.show_text2(s)

    def get_text0(self):
        s = self.text.get('1.0', 'end')
        return s

    def show_text1(self, s):
        if self.win1 is None:
            win = tk.Tk()
            win.title('ENTITY')
            win.rowconfigure(0, weight=1)
            win.columnconfigure(0, weight=1)
            w = 900
            h = 500
            x = 200
            y = 150
            win.geometry('%dx%d+%d+%d' % (w, h, x, y))
            self.win1 = win
            self.win1.protocol("WM_DELETE_WINDOW", self.quit1)
            self.text1 = tk.Text(self.win1)
            self.text1.grid(sticky='nsew')
            editorFont = Font(family="Arial", size=12)
            self.text1.configure(font=editorFont)
        self.text1.delete('1.0', END)
        self.text1.insert('1.0', s)

    def quit1(self):
        self.win1.destroy()
        self.win1 = None

    def get_text1(self):
        s = self.text1.get('1.0', 'end')
        return s

    def show_text2(self, s):
        if self.win2 is None:
            win = tk.Tk()
            win.title('XML')
            win.rowconfigure(0, weight=1)
            win.columnconfigure(0, weight=1)
            w = 900
            h = 500
            x = 400
            y = 300
            win.geometry('%dx%d+%d+%d' % (w, h, x, y))
            self.win2 = win
            self.win2.protocol("WM_DELETE_WINDOW", self.quit2)
            self.text2 = tk.Text(self.win2)
            self.text2.grid(sticky='nsew')
            editorFont = Font(family="Arial", size=12)
            self.text2.configure(font=editorFont)
        self.text2.delete('1.0', END)
        self.text2.insert('1.0', s)

    def quit2(self):
        self.win2.destroy()
        self.win2 = None
#################

    def delete_text(self):
        self.text.delete('1.0', END)
        self.delete_text1()
        self.delete_text2()

    def delete_text1(self):
        if self.text1 is not None:
            self.text1.delete('1.0', END)
        self.delete_text2()

    def delete_text2(self):
        if self.text2 is not None:
            self.text2.delete('1.0', END)

    def quit(self):
        self.win.quit()
        if self.win1 is not None:
            self.win1.quit()
        if self.win2 is not None:
            self.win2.quit()

    def open_tags(self):
        path = fd.askopenfilename(title='Scegli file tags', filetypes=[("tags", "*.csv")])
        if len(path) < 1:
            return
        # self.path_tags = self.set_abs_path(path)
        self.set_path_tags(path)
        self.show_title()

    def open_conf(self):
        path = fd.askopenfilename(title='Scegli file conf', filetypes=[("conf", "*.cnf")])
        if len(path) < 1:
            return
        self.parse_cnf(path)
        self.show_title()

    def open_file(self):
        path = fd.askopenfilename(title='Scegli un file', filetypes=[("text", "*.txt"), ('', '*.*')])
        if len(path) < 1:
            return
        self.set_paths(path)
        self.read_file0()

    def read_file0(self):
        self.text.delete('1.0', END)
        with open(self.path_file0, 'rt') as f:
            s = f.read()
            self.text.insert('1.0', s)
            self.show_title()

    def save_file_as(self):
        path = fd.asksaveasfilename(title='Dove Salvare')
        if len(path) < 1:
            return
        self.write_file(path)

    def save_file(self):
        if self.path_file0 is None:
            return
        self.write_file(self.path_file0)

    def write_file(self, path):
        with open(path, 'w') as f:
            s = self.text.get('1.0', 'end')
            f.write(s)
            os.chmod(path, 0o666)


def do_main(path_tags, path_file, path_cnf):
    tme = TeimEdit(path_tags, path_file, path_cnf)
    tme.open()


if __name__ == "__main__":
    print("author: %s" % (__author__))
    print("release: %s  %s" % (__version__, __date__))
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        dest="txt",
                        required=False,
                        default=None,
                        metavar="",
                        help="[-i <file input>] default: TEIM0.txt")
    parser.add_argument('-t',
                        dest="tag",
                        required=False,
                        default=None,
                        metavar="",
                        help="[-t <file tags>] default:TEIMTAGS.csv")
    parser.add_argument('-c',
                        dest="cnf",
                        required=False,
                        default=None,
                        metavar="",
                        help="[-c <file.cnf>] ")
    args = parser.parse_args()
    do_main(args.tag, args.txt, args.cnf)

    
