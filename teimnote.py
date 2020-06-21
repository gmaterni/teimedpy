#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
from pdb import set_trace
from lxml import etree
import os
import argparse
import sys
# from pdb import set_trace

__date__ = "24-05-2018"
__version__ = "0.1.1"
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

    """
    def add_to_xmlX(self):
        note_list = self.read_note()
        root = etree.parse(self.src_path)
        nds = root.findall('div')
        nd_last = nds[len(nds) - 1]
        for note in note_list:
            note_id = note[NOTE_ID]
            note_text = note[NOTE_TEXT]
            # note_xml = '<note xml:id="%s" >%s</note>' % (note_id, note_text)
            note_xml = '<note xml:id="%s" ><![CDATA[%s]]></note>' % (note_id, note_text)
            # print(note_xml)
            note_node = etree.XML(note_xml)
            nd_last.addnext(note_node)
        xml = etree.tostring(root, xml_declaration=None, encoding='unicode', pretty_print=True)
        with open(self.out_path, "w+") as f:
            xml_decl = "<?xml version='1.0' encoding='utf-8' standalone='yes'?>"
            f.write(xml_decl)
            f.write(xml)
        os.chmod(self.out_path, 0o666)
    """

    """
    def add_to_xml(self):
        note_list = self.read_note()
        note_src = ""
        for note in note_list:
            note_id = note[NOTE_ID]
            note_text = note[NOTE_TEXT]
            note_xml = '<note xml:id="%s" >%s<![CDATA[%s]]>%s</note>' % (note_id, os.linesep, note_text, os.linesep)
            note_src = note_src + note_xml
        with open(self.src_path, "rt") as f:
            xml_src = f.read()
        xml_new = xml_src.replace('</TEI>', note_src) + "</TEI>"
        with open(self.out_path, "w+") as f:
            f.write(xml_new)
        os.chmod(self.out_path, 0o666)
    """

    def add_to_xml(self):
        note_list = self.read_note()
        fou = open(self.out_path, 'w+')
        with open(self.src_path, "rt") as f:
            for line in f:
                if line.find('</TEI>') > -1:
                    for note in note_list:
                        note_id = note[NOTE_ID]
                        note_text = note[NOTE_TEXT]
                        fou.write('<teimed_note xml:id="%s" >' % (note_id))
                        fou.write(os.linesep)
                        fou.write(note_text.strip())
                        fou.write(os.linesep)
                        fou.write('</teimed_note>')
                        fou.write(os.linesep)
                fou.write(line)
        fou.close()
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
    parser.add_argument('-n', dest="note", required=True, metavar="", help="-n <file note> ")
    parser.add_argument('-i', dest="src", required=True, metavar="", help="-i <file input>")
    parser.add_argument('-o', dest="out", required=True, metavar="", help="-o <file output>")
    args = parser.parse_args()
    if args.src == args.out:
        print("Name File output errato")
        sys.exit(0)
    do_main(args.note, args.src, args.out)
