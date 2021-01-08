#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
import sys
from ualog import Log
# import pprint


__date__ = "09-01-2021"
__version__ = "0.9.0"
__author__ = "Marta Materni"

logerr = Log('w')
logdeb = Log('w')

"""
pprn = pprint.PrettyPrinter(indent=1, width=130)


def pp_data(data):
    if data is None:
        return ""
    s = pprint.pformat(data, indent=0, width=80)
    return s
"""

xml_top = """<?xml version='1.0' encoding='utf-8' standalone='yes'?>
    <TEI>        """
xml_bottom = """    </TEI>"""

SP = " "
SPSP = "  "
SPw = "|"   # carattere temp di SP  dentro tag
CU = "_"
CUw = "@@"   # carattere temp di CU per parole composte
Cw1 = "$$"   # carattere  temporaneo
Cw2 = "§§ "  # carattere  temporaneo
CNw = "$"    # carattere temp per note

# segmentazione
AP = "'"   # <w ana="#elis">$</w>
SL = "\\"  # <w ana="#encl">$</w>
CR = "°"  # <w ana="#degl">$</w>
# tags
OPPB = "<pb"
OPCB = "<cb"
OPLG = "<lg"
OPL = "<l"
OPW = "<w"
OPC = "<pc"
OPTR = "<ptr"


class AddLineWordTag(object):
    def __init__(self, path_src, path_out, sigla_scrpt, ids_start):
        self.path_src = path_src
        self.path_out = path_out

        path_err = path_out.replace(".xml", "_err.log")
        logerr.open(path_err, out=1)

        path_deb = path_out.replace(".xml", "_deb.log")
        logdeb.open(path_deb, out=0)

        self.sigla_scrp = sigla_scrpt
        self.pb_num = 1
        self.cb_num = 1
        self.lg_num = 1
        self.l_num = 1
        self.line_num = 1
        self.pc_num = 1
        self.ptr_num = 1
        self.set_ids_start(ids_start)
        self.LINE_NUM = 0
        self.NLINE = 0
        self.DEBUG = False

    def set_ids_start(self, ids_start):
        if ids_start.strip() == "":
            return
        tgs = ids_start.split(",")
        for tg in tgs:
            kv = tg.split(":")
            k = kv[0]
            v = kv[1]
            if k == "pb":
                self.pb_num = int(v)
            elif k == "cb":
                self.cb_num = int(v)
            elif k == "lg":
                self.lg_num = int(v)
            elif k == "ptr":
                self.ptr_num = int(v)
            elif k == "l":
                self.l_num = int(v)
                self.line_num = 1

    def is_div(self, line):
        s = line.strip()
        n1 = s.count("<")
        n2 = s.count(">")
        n = n1 + n2
        oc = s[0] == "<" and s[-1] == ">"
        div = n == 2 and oc
        return div

    def preserve_note(self, line):
        p0 = line.find("<note")
        p1 = line.find("</note>")
        s0 = line[0:p0]
        s1 = line[p0:p1]
        s2 = line[p1:]
        s1 = s1.replace(" ", CNw, -1)
        t = s0 + s1 + s2
        t = t.replace("<note", " <note", -1).replace("</note>", "</note> ", -1)
        return t

    def set_div_id(self, line):
        if line.find(OPPB) > -1:
            id = '<pb xml:id="%spb%s" ' % (self.sigla_scrp, self.pb_num)
            line = line.replace("<pb", id)
            self.pb_num += 1
            return line
        if line.find(OPCB) > -1:
            id = '<cb xml:id="%scb%s" ' % (self.sigla_scrp, self.cb_num)
            line = line.replace("<cb", id)
            self.cb_num += 1
            return line
        if line.find(OPLG) > -1:
            id = '<lg xml:id="%slg%s" ' % (self.sigla_scrp, self.lg_num)
            line = line.replace("<lg", id)
            self.lg_num += 1
            return line
        return line

    def set_line_id(self, line):
        s = '<l n="%s" xml:id="%sl%s">%s</l> %s' % (
            self.line_num,
            self.sigla_scrp,
            self.l_num,
            line,
            os.linesep,
        )
        self.l_num += 1
        self.line_num += 1
        return s

    def set_words_id(self, line):
        wn = line.count(OPW)
        if wn == 0:
            return line
        for i in range(0, wn):
            n = i + 1
            sid = '%s xml:id="%sl%sw%s" ' % (
                Cw1, self.sigla_scrp, self.l_num, n)
            line = line.replace(OPW, sid, 1)
        line = line.replace(Cw1, OPW, -1)
        return line

    def set_pcs_id(self, line):
        pn = line.count(OPC)
        if pn == 0:
            return line
        for i in range(0, pn):
            n = i + 1
            sid = '%s xml:id="%sl%spc%s" ' % (
                Cw1, self.sigla_scrp, self.l_num, n)
            line = line.replace(OPC, sid, 1)
        line = line.replace(Cw1, OPC, -1)
        return line

    def set_ptr_id(self, line):
        ptr = line.count(OPTR)
        if ptr == 0:
            return line
        for i in range(0, ptr):
            sid = '%s xml:id="%sptr%s" ' % (Cw2, self.sigla_scrp, self.ptr_num)
            line = line.replace(OPTR, sid, 1)
            self.ptr_num += 1
        line = line.replace(Cw2, OPTR, -1)
        return line

    # <w>text<c>n</c><sp><c>x</c></sp>text<c>a</c></w>
    def line_text_check(self, src, liv):
        le = len(src) - 1
        txtliv = -1
        tg = False
        tcop = False
        ls = []
        txtls = []
        for i, c in enumerate(src):
            cn = src[i + 1] if i < le else " "
            if c == "<":
                tg = True
                if cn == "/":
                    tcop = False
                    txt = "".join(ls)
                    txtls.append(txt)
                    ls = []
                else:
                    tcop = True
                    ls = []
            if tg is False and txtliv == liv:
                ls.append(c)
            if c == ">":
                tg = False
                if tcop:
                    txtliv += 1
                else:
                    txtliv -= 1
        return txtls

    def line_text_check_log(self, line):
        for liv in range(1, 8):
            s = self.line_text_check(line, liv)
            if len("".join(s)) > 0:
                logdeb.log("%s) %s" % (liv, s))

    def set_w_type(self, w):
        # print("w " + w)
        ls = w.split('<w')
        ws = []
        ws.append(ls[0])
        for x in ls[1:]:
            s = '<w' + x
            # SL "\"
            if s.find(SL) > -1:
                s = s.replace(SL, "", -1)
                s = s.replace("<w", '<w ana="#encl" ')
            # AP "'" apice
            elif s.find(AP) > -1:
                s = s.replace(AP, "", -1)
                s = s.replace("<w", '<w ana="#elis" ')
            # CR "°"
            elif s.find(CR) > -1:
                s = s.replace(CR, "", -1)
                s = s.replace("<w", '<w ana="#degl" ')
            ws.append(s)
            w = ''.join(ws)
        return w

    def add_line_word(self, line):
        if line.find("<note") > -1:
            line = self.preserve_note(line)

        # aggiunge spazio a sinistra per isolare i tag della punteggiatura
        line = line.replace("<pc", " <pc", -1)
        line = line.replace("<ptr", " <ptr", -1)

        # aggiunge spazio a destra
        line = line.replace("</pc>", "</pc> ", -1)
        line = line.replace("</ptr>", "</ptr> ", -1)

        # stacca parentesi graffa quando fuori da w
        line = line.replace(">}", "> } ", -1)

        # attacca laparentesi graffa di apetura alla parola
        line = line.replace("{ ", "{", -1)
        line = line.replace("{_ ", "{_", -1)

        # attacca laparentesi QUADRA di apetura alla parola
        line = line.replace("[ ", "[", -1)
        line = line.replace("[_ ", "[_", -1)

        # elimina doppi SP
        line = line.replace(SPSP, SP, -1)
        line = line.replace(SPSP, SP, -1)
        lst = []
        
        # preparazione caratteri linea per split SP
        is_in_tag = False
        p=""
        for c in line:
            if c == "<":
                is_in_tag = True
            if c == ">":
                is_in_tag = False
                lst.append(c)
                continue
            if is_in_tag:
                c = SPw if c == SP else c
            else:
                # trasfroma CU in CUw fuori i tag escluso [_ {_ 
                c = CUw if (c == CU and p not in "[{" ) else c
            p = c
         
            lst.append(c)
        s = "".join(lst).strip()
        words = []
        ws = s.split(SP)
        for i, w in enumerate(ws):
            s = w.strip().replace(SPw, SP, -1)
            # segop, s = self.add_seg_open(s)
            segop=""
            # segcl, s = self.add_seg_close(s)
            segcl=""
            # trasforma CUw in SP
            # gestione paroloe composte  es  for_se => for se
            s = s.replace(CUw, SP, -1)
            if s.find("<pc") > -1:
                words.append("%s%s%s" % (segop, s, segcl))
            elif s.find("<ptr") > -1:
                words.append("%s%s%s" % (segop, s, segcl))
            # espansioni che iniziano con <w
            elif s.find("<w") == 0:
                s = self.set_w_type(s)
                words.append("%s%s%s" % (segop, s, segcl))
            elif s.find("<w") > 0:
                s = self.set_w_type(s)
                words.append("%s%s%s" % (segop, s, segcl))
            # gestione note
            elif s.find("<note") > -1:
                s = s.replace(CNw, " ", -1)
                words.append(s)         
            # SL "\"
            elif s.find(SL) > -1:
                s = s.replace(SL, "", -1)
                words.append('%s<w ana="#encl">%s</w>%s' % (segop, s, segcl))
            # AP "'" apice
            elif s.find(AP) > -1:
                s = s.replace(AP, "", -1)
                words.append('%s<w ana="#elis">%s</w>%s' % (segop, s, segcl))
            # CR "°"
            elif s.find(CR) > -1:
                s = s.replace(CR, "", -1)
                words.append('%s<w ana="#degl">%s</w>%s' % (segop, s, segcl))
            elif s.strip() == "":
                words.append("%s" % (segcl))
            else:
                words.append("%s<w>%s</w>%s" % (segop, s, segcl))

        line = "".join(words)
        line = self.set_words_id(line)
        line = self.set_pcs_id(line)
        line = self.set_ptr_id(line)
        line = self.set_line_id(line)
        line = line.replace("  ", SP, -1)
        line = line.replace("> <", "><", -1)

        logdeb.log("")
        logdeb.log(line.strip())
        self.line_text_check_log(line)
        for w in words:
            logdeb.log(w.strip())
            self.line_text_check_log(w)

        if line.find("kl18w1") < -1:
            pass
            # print("***** %s" % (self.NLINE))
        self.NLINE += 1
        return line

    def addtags(self):
        fw = open(self.path_out, "w+")
        fw.write(xml_top)
        fw.write(os.linesep)
        self.LINE_NUM = 0
        with open(self.path_src, "r") as f:
            for line in f:
                self.LINE_NUM += 1
                line = line.replace("\ufeff", "")
                if line.strip() == "":
                    continue
                if self.is_div(line):
                    line = self.set_div_id(line)
                    fw.write(line)
                    continue
                s = self.add_line_word(line)
                fw.write(s)
        fw.write(xml_bottom)
        fw.close()
        os.chmod(self.path_out, 0o666)


def do_main(path_src, path_out, sigla_scrp, ids_start=""):
    alwp = AddLineWordTag(path_src, path_out, sigla_scrp, ids_start)
    alwp.addtags()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument(
        "-i",
        dest="src",
        required=True,
        metavar="",
        help="-i <file input>"
    )
    parser.add_argument(
        "-o",
        dest="out",
        required=True,
        metavar="",
        help="-o <file output>"
    )
    parser.add_argument(
        "-s",
        dest="sms",
        required=True,
        metavar="",
        help="-s <sigla mano scritto> (prefisso id)",
    )
    parser.add_argument(
        "-n",
        dest="ids",
        required=False,
        default="",
        metavar="",
        help="-n <'pb:1,cb:1,lg:1,l:1,ptr:1'>  (start id elementi)",
    )
    args = parser.parse_args()
    do_main(args.src, args.out, args.sms, args.ids)
