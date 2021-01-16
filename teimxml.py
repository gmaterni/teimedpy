#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
from ualog import Log

__date__ = "08-01-2021"
__version__ = "0.9.1"
__author__ = "Marta Materni"


loginfo = Log("w")
logerr = Log("w")


# pprn = pprint.PrettyPrinter(indent=1, width=130)
"""
def pp_data(data):
    if data is None:
        return ""
    s = pprint.pformat(data, indent=0, width=80)
    return s
"""

TAG_MAX_LEN = 30
ARGS_MAX_LEN = 60

COL_TYPE = "tp"
COL_NAME = "name"
COL_VAL = "val"
COL_NARG = "narg"

TAG_NAME = "name"
TAG_ARGS = "args"
TAG_LEN = "len"
TAG_TXT = "txt"

CH_EC = '&'
CHS_TGU = "éèàùòìÀÈÉÒÙÌ"
CHS_TGS = "&*^`~"
CHS_TAG = CHS_TGS + CHS_TGU


class Med2Xml(object):

    def __init__(self, src, tag, out):
        self.path_src = src
        self.path_tag = tag
        self.path_out = out
        self.delimiter = '|'
        self.tags = None
        self.LINE_TEXT = ""
        self.LINE_NUM = 0
        out_name = out.split('.')[0]
        path_info = "%s.log" % (out_name)
        path_err = "%s.ERR.log" % (out_name)
        loginfo.open(path_info, out=0)
        logerr.open(path_err, out=1)

    def read_tags(self):
        """ Lettura tags da csv
        formato:
        {
        name1:{'tp':tipo,'tag_txt':espressione1,'narg':2}
        name2:{'tp':tipo,'tag_txt':espressione2,'narg':3}
        }
        """
        self.tags = {}
        with open(self.path_tag, "rt") as f:
            for line in f:
                if line.strip() == '':
                    continue
                cols = line.split(self.delimiter)
                # name = re.sub(r'[^\x00-\x7F]', '', fs[0])
                tag_type = cols[0].strip()
                tag_name = cols[1].strip()
                tag_val = cols[2].strip()
                args_num = tag_val.count('$')
                tag = {}
                tag[COL_TYPE] = tag_type
                tag[COL_VAL] = tag_val
                tag[COL_NARG] = args_num
                self.tags[tag_name] = tag

    def get_args_end(self, line_num, line, start, max_len):
        pe = None
        s = line[start:]
        pa = 0
        try:
            for i, c in enumerate(s):
                if c == '(':
                    pa = pa + 1
                if c == ')':
                    if pa == 1:
                        pe = i + start
                        break
                    pa = pa - 1
            if pe is None:
                raise Exception("")
        except Exception:
            logerr.log("ERROR get_args_end().  Not found ')' ")
            logerr.log("%s)%s" % (line_num, line.strip()))
            return None
        return pe

    # tag inserita nel testo
    # &tag_name;(arg1,arg2,..)
    # {'name':tag_name,'args':[arg1,arg2,..],'len':num char}
    def get_tag_ent(self, line_num, line, index):
        tag_txt = {}
        end = None
        try:
            end = line.index(';', index, index + TAG_MAX_LEN)
        except Exception:
            logerr.log("ERROR  get_tag_ent()  ';'' Not Found. ")
            logerr.log(f"line num:{line_num} line:{line}")
            return None
        name = line[index:end + 1]
        tag_txt[TAG_NAME] = name
        pa_start = -1
        """
        try:
            pa_start = line.index('(', end, end + 2)
        except Exception:
            pa_start = -1
        """
        pa_start = line.find('(', end, end+2)
        if pa_start > 0:
            end = self.get_args_end(line_num, line, pa_start, ARGS_MAX_LEN)
            s = line[pa_start + 1:end]
            ls = []
            p = False
            for c in list(s):
                if c == '(':
                    p = True
                if c == ')':
                    p = False
                if p and c == ',':
                    c = '|'
                ls.append(c)
            s = "".join(ls)
            ls = s.split(',')
            args = []
            for a in ls:
                args.append(a.replace('|', ',', -1))
        else:
            args = []
        tag_txt[TAG_ARGS] = args
        tag_txt[TAG_LEN] = end - index + 1
        tag_txt[TAG_TXT] = line[index:end + 1]
        return tag_txt

    # tag  precedute da un carattere es: ^a  ^ t
    # tag di singoli caratteri  es:  è ù
    def get_tag_char_name(self, line, index, c):
        tag_txt = {}
        end = index + 1
        if c in CHS_TGU:
            name = line[index:end].strip()
            tag_txt[TAG_LEN] = 1
        else:
            name = line[index:end + 1].strip()
            tag_txt[TAG_LEN] = 2
        tag_txt[TAG_NAME] = name
        tag_txt[TAG_ARGS] = []
        tag_txt[TAG_TXT] = name
        tag_txt[TAG_NAME] = name
        return tag_txt

    # .tag per punteggiatura
    # {'name':'.','args':[],'len':1}
    def get_tag_pc(self, line, index):
        tag_txt = {}
        name = line[index]
        tag_txt[TAG_NAME] = name
        tag_txt[TAG_ARGS] = []
        tag_txt[TAG_LEN] = 1
        tag_txt[TAG_TXT] = name
        return tag_txt

    def build_tag_val_args(self, tag_txt, tag_data):
        args = tag_txt[TAG_ARGS]
        narg = tag_data[COL_NARG]
        tag_val = tag_data[COL_VAL]
        #
        l_num=tag_txt[COL_NAME]
        l_text=tag_data[COL_NARG]
        if len(args) != narg:
            logerr.log("Warning num.args !")
            logerr.log(f"{self.LINE_NUM}) {self.LINE_TEXT.strip()}")
            logerr.log(f"{l_num} num.args:{l_text}")
            logerr.log("")
        for arg in args:
            if arg != '':
                tag_val = tag_val.replace('$', arg, 1)
        return tag_val

    def log_tag(self, liv, line_num, line, tag_data, tag_txt, tag_val):
        if liv == 0:
            s = '{:<40}: {}'.format(tag_txt[TAG_TXT], tag_val)
        else:
            s = '{:<40}: {}'.format(tag_txt[TAG_TXT], tag_val)
        loginfo.log(s)

    def log_error(self, err, line_num, line, tag_name):
        tag_name = '' if tag_name is None else tag_name
        logerr.log("%s  tag:%s Not Found." % (err, tag_name))
        logerr.log("%s) %s" % (line_num, line))
        # sys.exit()

    def compose(self, liv, line, line_num):
        note_idx = line.rfind('<note')
        line_len = len(line)
        lst = []
        i = 0
        while True:
            c = line[i]
            # c==&
            if c == CH_EC:
                tag_data = None
                tag_name = ""
                tag_txt = ""
                try:
                    tag_txt = self.get_tag_ent(line_num, line, i)
                    tag_name = tag_txt[TAG_NAME]
                    tag_name_csv = tag_name.replace(
                        CH_EC, '').replace(';', '').strip()
                    tag_data = self.tags.get(tag_name_csv, None)
                except Exception:
                    tag_data = None
                if tag_data is None:
                    self.log_error('ERROR1', line_num, line, tag_name)
                    tag_data = {'tp': 'err',
                                'val': '<err>ERROR1</err>', 'narg': 0}
                tag_val = self.build_tag_val_args(tag_txt, tag_data)
                self.log_tag(liv, line_num, line, tag_data, tag_txt, tag_val)
                for c in tag_val:
                    lst.append(c)
                i += (tag_txt[TAG_LEN] - 1)
            # CHS_TAG:  # !*^`~"+"àéù""
            elif c in CHS_TAG:
                if liv > 0 and c in CHS_TGU and note_idx > -1 and note_idx < i:
                    lst.append(c)
                else:
                    tag_txt = self.get_tag_char_name(line, i, c)
                    tag_name = tag_txt[TAG_NAME]
                    tag_data = self.tags.get(tag_name, None)
                    if tag_data is None:
                        self.log_error('ERROR2', line_num, line, tag_name)
                        tag_data = {'tp': 'err',
                                    'val': '<err>ERRROR2</err>', 'narg': 0}
                    tag_val = tag_data[COL_VAL]
                    self.log_tag(liv, line_num, line,
                                 tag_data, tag_txt, tag_val)
                    for c in tag_val:
                        lst.append(c)
                    i += (tag_txt[TAG_LEN] - 1)
            # non sostituisce per il secondo compose sugli argomenti quando liv==1
            elif liv == 0 and c in [',', '.', ';', '?', ':', '!']:
                tag_txt = self.get_tag_pc(line, i)
                tag_name = tag_txt[TAG_NAME]
                tag_data = self.tags.get(tag_name, None)
                if tag_data is None:
                    self.log_error('ERROR3', line_num, line, tag_name)
                    tag_data = {'tp': 'err',
                                'val': '<err>ERRROR3</err>', 'narg': 0}
                tag_val = tag_data[COL_VAL]
                self.log_tag(liv, line_num, line, tag_data, tag_txt, tag_val)
                for c in tag_val:
                    lst.append(c)
                i += (tag_txt[TAG_LEN] - 1)
            else:
                lst.append(c)
            i += 1
            if i >= line_len:
                break
        return "".join(lst)

    # "&*^`~"+ "éàù"
    def find_chs_set(self, s):
        tf = False
        for c in CHS_TAG:
            if s.find(c) > -1:
                tf = True
                break
        return tf

    def parse_txt(self):
        self.read_tags()
        fout = open(self.path_out, "w")
        line_num = 0
        with open(self.path_src, "rt") as f:
            for line in f:
                line = line.replace('\ufeff', '', -1)
                line = line.replace('\t', ' ', -1)
                pc = line.find('<!')
                if pc > -1:
                    line = line[0:pc - 1]
                    line = line.strip()
                    line = line + os.linesep
                line_num += 1
                self.LINE_TEXT = line
                self.LINE_NUM = line_num
                loginfo.log("%s%s) %s" % (os.linesep, line_num, line.strip()))
                try:
                    s = self.compose(0, line, line_num)
                except Exception as e:
                    logerr.log("ERROR compose ")
                    logerr.log(str(e))
                    logerr.log("%s)%s." % (line_num, line))
                    continue
                loginfo.log("=>  %s" % (s.strip()))
                # chiamata per argomenti funzioni
                if self.find_chs_set(s):
                    loginfo.log("%s] %s" % (line_num, s.strip()))
                    s = self.compose(1, s, line_num)
                    loginfo.log("->  %s" % (s.strip()))
                    if self.find_chs_set(s):
                        loginfo.log("%s] %s" % (line_num, s.strip()))
                        s = self.compose(1, s, line_num)
                        loginfo.log(":>  %s" % (s.strip()))
                fout.write(s)
        fout.close()
        os.chmod(self.path_out, 0o666)

    def check_txt(self):
        with open(self.path_src, "rt") as f:
            src = f.readlines()
        with open(self.path_out, "rt") as f:
            for i, line in enumerate(f):
                if line.find('&') > -1:
                    logerr.log("ERROR tag & ")
                    r = src[i].strip()
                    s = "%s) %s" % (i + 1, r)
                    logerr.log(s)
                    logerr.log(line)
                    logerr.log("")


def do_main(path_src, path_tag, path_out):
    txtv = Med2Xml(path_src, path_tag, path_out)
    txtv.parse_txt()
    txtv.check_txt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument('-t',
                        dest="tag",
                        required=False,
                        default="tags.csv ",
                        metavar="",
                        help="[-t <file tags>] default:tags.csv")
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
    do_main(args.src, args.tag, args.out)
