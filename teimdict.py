#!/usr/bin/env python3
# -*- coding: utf-8 -*-e
"""
esporta il dizionario di un testo
tutte le parole e la loro frequenza
"""
import os
import argparse
import sys

__date__ = "19-01-2021"
__version__ = "0.2.2"
__author__ = "Marta Materni"


tab_sep = '|'
col_word = 0
col_num = 1
col_info = 2


class ExpDict(object):

    def __init__(self):
        self.tab = None

    def add_line(self, line):
        line = line.replace('.', ' . ', -1)
        line.replace(';', ' ; ', -1)
        line.replace(',', ' , ', -1)
        # line=line.replace('/',' / ',-1)
        # line = line.replace('|', '!', -1)
        line = line.replace('\"', '', -1)
        line.replace('\'', '')
        line.replace('(', '')
        line.replace(')', '')
        rs = line.split(' ')
        for w in rs:
            word = w.strip()
            if word == '':
                continue
            row = self.tab.get(word, None)
            if row is None:
                row = [word, '1', '']
                self.tab[word] = row
            else:
                n = int(row[col_num]) + 1
                sn = str(n)
                row[col_num] = sn
                self.tab[word] = row

    def export(self, src_path, out_path):
        self.tab = dict()
        with open(src_path, "r") as f:
            for line in f:
                if line.strip() == '':
                    continue
                self.add_line(line)

        rows = self.tab.values()
        rs = sorted(rows, key=lambda x: (x[0]))
        fw = open(out_path, "w+")
        for row in rs:
            line = tab_sep.join(row)
            fw.write(line)
            fw.write(os.linesep)
        fw.close()
        os.chmod(out_path, 0o666)


def do_main(src_path, out_path=None):
    expdict = ExpDict()
    expdict.export(src_path, out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument('-i', dest="src", required=True, metavar="", help="-i <file input>")
    parser.add_argument('-o', dest="out", required=True, metavar="", help="-o <file output>")
    args = parser.parse_args()
    do_main(args.src, args.out)
    # os.chmod(args.lf, 0o666)
