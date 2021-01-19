#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pdb import set_trace
import os
import argparse
import sys
import re
from xml_const import *

__date__ = "19-01-2021"
__version__ = "0.9.4"
__author__ = "Marta Materni"


NOTE_TYPE = "note_type"
NOTE_ID = "note_id"
NOTE_TEXT = "note_text"

class AddNote(object):

    def __init__(self, src_path, out_path, note_path):
        self.src_path = src_path
        self.out_path = out_path
        self.note_path = note_path
        self.delimiter = '|'

    def read_note(self):
        note_list = []
        item = {}
        txt = ""
        with open(self.note_path, "rt") as f:
            for line in f:
                if line.strip() == '':
                    continue
                if line.find(self.delimiter) > -1:
                    item[NOTE_TEXT] = txt
                    note_list.append(item)
                    item = {}
                    cols = line.split(self.delimiter)
                    item[NOTE_TYPE] = cols[0].strip()
                    item[NOTE_ID] = cols[1].strip()
                    txt = cols[2].strip()
                    continue
                txt = txt + os.linesep + line.strip()
        item[NOTE_TEXT] = txt
        note_list.append(item)
        del note_list[0]
        return note_list

    def add_to_xml(self):
        note_list = self.read_note()
        ls = []
        for note in note_list:
            note_id = note[NOTE_ID]
            note_text = note[NOTE_TEXT]
            text = note_text.strip().replace(os.linesep, " ")
            s = f'<teimed_note xml:id="{note_id}">{text}</teimed_note>'
            ls.append(s)
        note = os.linesep.join(ls)
        #
        with open(self.src_path, "rt") as f:
            xml = f.read()
        xml_sp = re.split(BODY_BOTTOM_PATTERN, xml)
        with open(self.out_path, 'w') as f:
            f.write(xml_sp[0])
            f.write(BODY_BOTTOM+os.linesep)
            f.write(BACK_TOP+os.linesep)
            f.write(NOTE_TOP+os.linesep)
            f.write(note)
            f.write(os.linesep+NOTE_BOTTOM+os.linesep)
            f.write(BACK_BOTTOM+os.linesep)
            f.write(xml_sp[1])
        os.chmod(self.out_path, 0o666)


def do_main(note_path, src_path, out_path):
    add_note = AddNote(src_path, out_path, note_path)
    add_note.add_to_xml()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument('-n',
                        dest="note",
                        required=True,
                        metavar="",
                        help="-n <file note> ")
    parser.add_argument('-i',
                        dest="src",
                        required=True,
                        metavar="",
                        help="-i <file input>")
    parser.add_argument('-o',
                        dest="out",
                        required=True,
                        metavar="",
                        help="-o <file output>")
    args = parser.parse_args()
    if args.src == args.out:
        print("Name File output errato")
        sys.exit(0)
    do_main(args.note, args.src, args.out)
