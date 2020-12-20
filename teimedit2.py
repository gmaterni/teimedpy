#!/usr/bin/env python3
# coding: utf-8

# from pdb import set_trace
import argparse
from teimxml import do_main as do_main_xml
from teimlineword2 import do_main as do_main_lineword
from teimxmllint import do_main as do_main_xmllint
from teimspan2 import do_main as do_main_span
from teimnote import do_main as do_main_note
import os
import json
import tkinter as tk
from tkinter.font import Font
import tkinter.filedialog as fd
from tkinter import END
import shutil
# import tkinter.messagebox as tkMessageBox
# from tkinter.filedialog import askopenfile
# from tkinter import *

__date__ = "03-11-2020"
__version__ = "0.6.0"
__author__ = "Marta Materni"


class TeimEdit(object):

    def __init__(self, path_tags=None, path_text=None, path_conf=None,path_note=None):
        self.read_start = (path_text is not None)
        #
        self.path_tags = None
        self.path_text = None
        self.path_file1_text = None
        self.path_file2_xml = None
        self.path_file3_xml = None
        self.path_file4_xml = None
        self.path_file5_xml = None
        self.path_conf = None
        self.path_note = None
        #
        self.set_path_tags(path_tags)
        self.set_paths(path_text)
        self.idman = 'k'
        self.parse_cnf(path_conf)
        self.set_path_note(path_note)
        #
        self.win = None
        self.text = None
        self.win1 = None
        self.text1 = None
        self.win2 = None
        self.text2 = None
        self.win3 = None
        self.text3 = None

    def set_abs_path(self, bname):
        pwd = os.path.abspath("")
        abs_path = os.path.join(pwd, bname)
        return abs_path

    def set_path_tags(self, path_tags):
        if path_tags is None:
            path_tags = self.set_abs_path('TEIMTAGS.csv')
        self.path_tags = self.set_abs_path(path_tags)
        print(self.path_tags)

    def set_path_note(self, path_note):
        if path_note is None:
            path_note = self.set_abs_path('NOTE.csv')
        self.path_note = self.set_abs_path(path_note)
        print(self.path_note)

    def set_paths(self, path_file0_text):
        # set_trace()
        if path_file0_text is None:
            path_file0_text = self.set_abs_path('TEIM0.txt')
        self.path_text = self.set_abs_path(path_file0_text)
        print(self.path_text)
        self.path_file1_text = self.path_text.replace('.txt', '_1.txt')
        print(self.path_file1_text)
        self.path_file2_xml = self.path_text.replace('.txt', '_2.xml')
        print(self.path_file2_xml)
        self.path_file3_xml = self.path_text.replace('.txt', '_3.xml')
        print(self.path_file3_xml)
        self.path_file4_xml = self.path_text.replace('.txt', '_4.xml')
        print(self.path_file4_xml)
        self.path_file5_xml = self.path_text.replace('.txt', '_5.xml')
        print(self.path_file5_xml)

    def parse_cnf(self, path_conf):
        if path_conf is not None:
            self.path_conf = self.set_abs_path(path_conf)
            with open(path_conf, "r") as f:
                txt = f.read()
            js = json.loads(txt)
            id = js['idman']
            self.idman = id
        else:
            self.path_conf = ""

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
        fm = tk.Menu(mb)

        fm.add_command(label='Save Text', command=self.save_text)
        fm.add_command(label='Save Twxt As...', command=self.save_text_as)

        fm.add_separator()
        fm.add_command(label='Open Text', command=self.open_text)
        fm.add_command(label='Open Tags', command=self.open_tags)
        fm.add_command(label='Open Conf', command=self.open_conf)
        fm.add_command(label='Open Note', command=self.open_note)

        fm.add_separator()
        fm.add_command(label='Elab.Entity', command=self.elab_teimxml)
        fm.add_command(label='Elab. XML', command=self.elab_teimlw)

        fm.add_separator()
        fm.add_command(label='Del All', command=self.delete_text)
        fm.add_command(label='Del Entity', command=self.delete_entity)
        fm.add_command(label='Del XML', command=self.delete_xml)
        fm.add_command(label='Del Log', command=self.delete_log)

        fm.add_separator()
        fm.add_command(label='Exit', command=self.quit)
        # orizontale
        mb.add_cascade(label='TeiMed', menu=fm)

        mb.add_separator()
        mb.add_command(label='  Open: Text', command=self.open_text)
        mb.add_command(label='Tags', command=self.open_tags)
        mb.add_command(label='Conf.', command=self.open_conf)
        mb.add_command(label='Note', command=self.open_note)

        mb.add_separator()
        mb.add_command(label='       Elab.: Entity', command=self.elab_teimxml)
        mb.add_command(label='XML', command=self.elab_teimlw)
        """
        mb.add_separator()
        mb.add_command(label='Del Text', command=self.delete_text)
        mb.add_command(label='Del Entity', command=self.delete_entity)
        mb.add_command(label='Del XML', command=self.delete_xml)
        """
        self.show_text1("")
        self.show_text2("")
        self.init_log()
        if self.read_start:
            self.read_file_text()
        tk.mainloop()

    #########################
    # TEI

    def show_title(self):
        text_name = os.path.basename(self.path_text)
        tags_name = os.path.basename(self.path_tags)
        conf_name = ""
        if self.path_conf != "":
            conf_name = os.path.basename(self.path_conf)
        title = f"text:{text_name}    tags:{tags_name}   mano:{conf_name}"
        self.win.title(title)

    def init_log(self):
        self.show_text3("")
        text_name = os.path.basename(self.path_text)
        tags_name = os.path.basename(self.path_tags)
        conf_name = os.path.basename(self.path_conf)
        note_name = os.path.basename(self.path_note)
        text1_name = os.path.basename(self.path_file1_text)
        xml2_name = os.path.basename(self.path_file2_xml)
        xml3_name = os.path.basename(self.path_file3_xml)
        xml4_name = os.path.basename(self.path_file4_xml)
        xml5_name = os.path.basename(self.path_file5_xml)
        logs = [
            "  ",
            f" text : {text_name}",
            f" tags : {tags_name}",
            f" mano.: {conf_name}",
            f" note : {note_name}",
            "---------"
            " ",
            f"entity: {text1_name}",
            f"xml: {xml2_name}",
            f"+ span: {xml3_name}",
            f"+ note: {xml4_name}",
            f"format: {xml5_name}",
            "---------"
            " ",
        ]
        s = os.linesep.join(logs)
        self.text3.delete('1.0', END)
        self.text3.insert('1.0', s)

    """
    def add_log(self, s):
        self.text3.insert('1.0', os.linesep)
        self.text3.insert('1.0', s)
    """

    def elab_teimxml(self):
        s = self.text.get('1.0', 'end')
        with open(self.path_text, 'w') as f:
            f.write(s)
        os.chmod(self.path_text, 0o666)
        do_main_xml(self.path_text, self.path_tags, self.path_file1_text)
        with open(self.path_file1_text, 'rt') as f:
            s = f.read()
        self.show_text1(s)
        self.init_log()

    """
        "teimxml.py -i fl_par_ep25.txt -t ./fl_teimed_tags.csv -o text1.txt",
        "teimlineword.py -i text1.txt -o text2.xml -s G -n 'pb:1,cb:1,lg:1,l:1'",
        "teimxmllint.py -i text2.xml -o text3.xml ",
        "teimspan.py -i text3.xml -o text4.xml",
        "teimnote.py -i text4.xml -o text5.xml -n ./fl_note.csv",
        "teimxmllint.py -i text5.xml -o fl_par_ep25.xml "
    """

    def elab_teimlw(self):
        do_main_lineword(self.path_file1_text, self.path_file2_xml, self.idman)

        # def do_main( src_path, out_path):
        do_main_span(self.path_file2_xml, self.path_file3_xml)

        # def do_main(note_path, src_path, out_path):
        try:
            do_main_note(self.path_note, self.path_file3_xml, self.path_file4_xml)
        except Exception as e:
            shutil.copyfile(self.path_file3_xml,self.path_file4_xml)
            os.chmod(self.path_file4_xml, 0o666)
            print("file Note nullo.")
        # def do_main(path_xml, path_out):
        do_main_xmllint(self.path_file4_xml, self.path_file5_xml)

        with open(self.path_file5_xml, 'rt') as f:
            s = f.read()
        self.show_text2(s)
        self.init_log()


    def quit1(self):
        self.win1.destroy()
        self.win1 = None

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

    def quit2(self ):
        self.win2.destroy()
        self.win2 = None

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

    def quit3(self):
        self.win3.destroy()
        self.win3 = None

    def show_text3(self, s):
        if self.win3 is None:
            win = tk.Tk()
            win.title('LOG')
            win.rowconfigure(0, weight=1)
            win.columnconfigure(0, weight=1)
            w = 250
            h = 400
            x = 1150
            y = 10
            win.geometry('%dx%d+%d+%d' % (w, h, x, y))
            self.win3 = win
            self.win3.protocol("WM_DELETE_WINDOW", self.quit3)
            self.text3 = tk.Text(self.win3)
            self.text3.grid(sticky='nsew')
            editorFont = Font(family="Arial", size=10)
            self.text3.configure(font=editorFont)
        self.text3.delete('1.0', END)
        self.text3.insert('1.0', s)


#################


    def delete_text(self):
        self.text.delete('1.0', END)
        self.delete_entity()
        self.delete_xml()
        self.delete_log()

    def delete_entity(self):
        if self.text1 is not None:
            self.text1.delete('1.0', END)
        self.delete_xml()

    def delete_xml(self):
        if self.text2 is not None:
            self.text2.delete('1.0', END)

    def delete_log(self):
        if self.text3 is not None:
            self.text3.delete('1.0', END)

    def quit(self):
        self.win.quit()
        if self.win1 is not None:
            self.win1.quit()
        if self.win2 is not None:
            self.win2.quit()
        if self.win3 is not None:
            self.win3.quit()

    def open_tags(self):
        path = fd.askopenfilename(
            title='Scegli file tags', filetypes=[("tags", "*.csv")])
        if len(path) < 1:
            return
        self.set_path_tags(path)
        self.show_title()
        self.init_log()

    def open_conf(self):
        path = fd.askopenfilename(
            title='Scegli file conf', filetypes=[("conf", "*.cnf")])
        if len(path) < 1:
            return
        self.parse_cnf(path)
        self.show_title()
        self.init_log()


    def open_note(self):
        path = fd.askopenfilename(
            title='Scegli file note', filetypes=[("note", "*.csv")])
        if len(path) < 1:
            return
        self.set_path_note(path)
        self.show_title()
        self.init_log()


    def open_text(self):
        path = fd.askopenfilename(title='Scegli un file',
                                  filetypes=[("text", "*.txt"), ('', '*.*')])
        if len(path) < 1:
            return
        self.set_paths(path)
        self.read_file_text()
        self.init_log()

    def read_file_text(self):
        self.text.delete('1.0', END)
        with open(self.path_text, 'rt') as f:
            s = f.read()
            self.text.insert('1.0', s)
            self.show_title()

    def save_text_as(self):
        path = fd.asksaveasfilename(title='Dove Salvare')
        if len(path) < 1:
            return
        self.write_file(path)

    def save_text(self):
        if self.path_text is None:
            return
        self.write_file(self.path_text)

    def write_file(self, path):
        with open(path, 'w') as f:
            s = self.text.get('1.0', 'end')
            f.write(s)
            os.chmod(path, 0o666)


def do_main(path_tags, path_file, path_cnf, path_note):
    tme = TeimEdit(path_tags, path_file, path_cnf, path_note)
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
                        help="[-c <file_sigla.cnf>] ")
    parser.add_argument('-n',
                        dest="note",
                        required=False,
                        default=None,
                        metavar="",
                        help="[-n <file_note.csv>] ")
    args = parser.parse_args()
    do_main(args.tag, args.txt, args.cnf, args.note)
