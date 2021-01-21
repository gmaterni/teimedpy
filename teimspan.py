#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggiunge span from=.. to=..
dicorso diretto:  {}
monologo: {__}
la parentesi chiusa può stare rispetto all'ultima patola
 o punto:
}word
word}
word }
.}
. }

agglutinazione:  []
agglutinazione incerta: [__]

damage: {0 0}
damage_lw: {1 1}
damage_medium: {2 2}
damage_high: {3 3}

"""
from pdb import set_trace
from lxml import etree
import os
import argparse
import sys
from ualog import Log
import pprint

__date__ = "21-01-2021"
__version__ = "0.10.1"
__author__ = "Marta Materni"


logspan = Log('w')
logerr = Log('w')


def pp(data):
    if data is None:
        return ""
    s = pprint.pformat(data, indent=2, width=120)
    return s+os.linesep


DATA_TYPE = "tp"
DATA_FROM = "from"
DATA_TO = "to"

# descr|from tag|to tag|log opn|log close
ROW_LST = [
    ['monologue', '{_', '_}', 'OMON', 'CMON'],
    ['damage', '{0%', '%0}', 'ODAM', 'CDAM'],
    ['damagel_low', '{1%', '%1}', 'ODAML', 'CDAML'],
    ['damage_medium', '{2%', '%2}', 'ODAMM', 'CDAMM'],
    ['damage_high', '{3%', '%3}', 'ODAMH', 'CDAMH'],
    ['directspeech', '{', '}', 'ODRD', 'CDRD'],
    ['agglutination_uncert', '[_', '_]', 'OAGLU', 'CAGLU'],
    ['agglutination', '[', ']', 'OAGLS', 'CAGLS']
]

OP = 'op'
CL = 'cl'
LOP = 'lop'
LCL = 'lcl'
TP = 'tp'
CTRL = 'ctrl'


class Addspan(object):

    def __init__(self, src_path, out_path):
        self.src_path = src_path
        self.out_path = out_path
        self.root = None
        self.span_data = None
        self.from_id_open = ''
        self.js = {}
        self.op_alter = []
        self.cl_alter = []
        self.op_lst = []
        self.cl_lst = []
        self.row_tag_lst = []
        path_span = out_path.replace('.xml', '_span.log')
        path_err = out_path.replace('.xml', '_ERR.log')
        logspan.open(path_span, out=0)
        logerr.open(path_err, out=1)

    def set_js(self, i):
        #  0        1       2      3       4
        # descr|from tag|to tag|log opn|log close
        row = self.row_tag_lst[i]
        self.js = {
            OP: row[1],
            CL: row[2],
            LOP: row[3],
            LCL: row[4],
            TP: row[0],
            CTRL: 0
        }
        self.op_lst=[]      # lista tag
        self.cl_lst = []
        self.op_alter = []  # tag alternativi a quello selezionato
        self.cl_alter = []
        lo = len(row[1])  # len tag open
        lc = len(row[2])  # len tag close
        # nella lista di controllo son settati i tag di lunghezza
        # > del tag selezionato
        for j, r in enumerate(self.row_tag_lst):
            self.op_lst.append(r[1])
            self.cl_lst.append(r[2])
            if j == i:
                continue
            if len(r[1]) > lo:
                self.op_alter.append(r[1])
            if len(r[2]) > lc:
                self.cl_alter.append(r[2])

    def set_from_id(self, nd_data):
        """
        estra tag span dal sorgente xml
        aggiunge un elemento a span_data
        setta self.from_id_open
        Args:
            nd_data (dict): dati del nodo xml
        """
        from_id = nd_data['id']
        tp = self.js[TP]
        item = {}
        item[DATA_TYPE] = tp
        item[DATA_TO] = ''
        item[DATA_FROM] = from_id
        self.span_data[from_id] = item
        self.from_id_open = from_id

    # setta to_id in span_data utilizzando from_id_open
    def set_to_id(self, nd_data):
        try:
            to_id = nd_data['id']
            item = self.span_data.get(self.from_id_open, None)
            if item is None:
                raise Exception(f"from_id_open:{self.from_id_open} Not Found.")
            item[DATA_TO] = to_id
        except Exception as e:
            logerr.log("ERROR teimspan set_id_to()")
            logerr.log(str(e)+os.linesep)
            if nd_data is not None:
                id = nd_data['id']
                tag = nd_data['tag']
                val = nd_data['val']
                s = 'id:{:<10} tag:{:<10} text:{}'.format(id, tag, val)
                logspan.log(s)
                logerr.log(s)
            sys.exit(1)

    # nodo precedente <w> or <pc>
    def get_prev(self, node):
        nd_prev = node.getprevious()
        tag = nd_prev.tag if type(nd_prev.tag) is str else "XXX"
        if tag.strip() in ['w', 'pc']:
            return nd_prev
        node_data = self.get_node_data(node)
        node_id = node_data['id']
        node_l = self.get_parent_l(node)
        nd_prev = node.getprevious()
        for nd in node_l.iterdescendants():
            tag = node.tag if type(node.tag) is str else "XXX"
            if tag.strip() in ['w', 'pc']:
                nd_data = self.get_node_data(nd)
                nd_id = nd_data['id']
                if nd_id == node_id:
                    break
                nd_prev = nd
        return nd_prev

    def log_open(self, nd):
        xml = self.xml2str(nd).strip()
        log = self.js[LOP]
        d = self.get_node_data(nd)
        id = f"from:{d['id']}"
        val = d['val']
        s = '{:<6}{:<15}{:<15}{}'.format(log, id, val, xml)
        s = s.replace(os.linesep, ' ', -1)
        logspan.log(s)

    def log_close(self, nd):
        xml = self.xml2str(nd).strip()
        log = self.js[LCL]
        d = self.get_node_data(nd)
        id = f"to  :{d['id']}"
        val = d['val']
        s = '{:<6}{:<15}{:<15}{}'.format(log, id, val, xml)
        s = s.replace(os.linesep, ' ', -1)
        logspan.log(s)
        logspan.log("")

    def control_open(self):
        self.js[CTRL] += 1
        if self.js[CTRL] > 1:
            log_cl = self.js[LCL]
            logspan.log(f" ERROR  missing {log_cl}")
            logspan.log("")
            self.js[CTRL] -= 1

    def control_close(self):
        self.js[CTRL] -= 1
        if self.js[CTRL] < 0:
            log_op = self.js[LOP]
            logspan.log(f" ERROR  missing {log_op}")
            self.js[CTRL] += 1

    """
    testo: 
        pipppo {% esempio
    pattern: {%
       testa tutti pattern di lunghezza >'{%' 
       qunidi '{'on viene testato 
       ritorna true
    pattern: {
        testa tutti i pattern dilunghezza > '{'
        viene trovato per '{%' 
        ritona false
    
    """

    def find_tag_from(self, s):
        t = self.js[OP]
        ok = False
        p = s.find(t)
        if p > -1:
            ok = True
            for x in self.op_alter:
                if s.find(x) > -1:
                    ok = False
                    break
        return ok

    def find_tag_to(self, s):
        t = self.js[CL]
        ok = False
        p = s.find(t)
        if p > -1:
            ok = True
            for x in self.cl_alter:
                if s.find(x) > -1:
                    ok = False
                    break
        return ok

    def fill_span(self):
        tp = self.js[TP]
        logspan.log(f">>>    {tp}"+os.linesep)
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                #
                if self.find_tag_from(val):
                    # print(f"{self.js[LOP]} {self.js[OP]}  {val} {text}")
                    self.set_from_id(nd_data)
                    self.control_open()
                    self.log_open(nd)
                #
                if self.find_tag_to(val):
                    if text.strip() == self.js[CL]:
                        # print(f"{self.js[OP]}_A {self.js[OP]}  {val} {text}")
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_to_id(nd_data)
                        self.control_close()
                        self.log_close(nd)
                    else:
                        # print(f"{self.js[LOP]}_B {self.js[OP]}  {val} {text}")
                        self.set_to_id(nd_data)
                        self.control_close()
                        self.log_close(nd)

    def xml2str(self, nd):
        if nd is None:
            return "<null/>"
        s = etree.tostring(nd,
                           xml_declaration=None,
                           encoding='unicode',
                           method="xml",
                           pretty_print=True,
                           with_tail=True,
                           standalone=None,
                           doctype=None,
                           exclusive=False,
                           inclusive_ns_prefixes=None,
                           strip_text=False)
        return s

    """
    def get_parent_l_xml(self,nd):
        l=self.get_parent_l(nd)
        s=self.xml2str(l)
        return s
    """

    def get_node_data(self, nd):
        tag = nd.tag if type(nd.tag) is str else "XXX"
        pid = tag.find('}')
        if pid > 0:
            tag = tag[pid + 1:].strip()
        text = "" if nd.text is None else nd.text.strip()
        val = ""
        for t in nd.itertext():
            val = val + t
        vid = ""
        if nd.attrib is not None:
            for k, v in nd.attrib.iteritems():
                pid = k.find('}id')
                if pid > -1:
                    vid = v
        nd_data = {
            'tag': tag.strip(),
            'id': vid,
            'text': text,
            'val': val
        }
        return nd_data

    # rtorna la linea <l> parent
    def get_parent_l(self, node):
        nd = None
        while node is not None:
            node = node.getparent()
            if node is None:
                break
            tag = node.tag if type(node.tag) is str else "XXX"
            if tag == 'l':
                nd = node
                break
        return nd

    # rtorna il <div> parent
    def get_span_parent(self, node):
        nd = None
        while node is not None:
            node = node.getparent()
            if node is None:
                break
            tag = node.tag if type(node.tag) is str else "XXX"
            if tag == 'div':
                nd = node
                break
        return nd

    def add_span(self, nd, sp_data):
        parent_node = self.get_span_parent(nd)
        if parent_node is None:
            logerr.log(
                "ERROR teimspan.py add_span() parent node <div>  Not Found.")
            sys.exit(1)
        #
        from_id = sp_data[DATA_FROM]
        to_id = sp_data[DATA_TO]
        tp = sp_data[DATA_TYPE]
        s = f'<span from="{from_id}" to="{to_id}" type="{tp}" />'
        # TODO log di xml span
        # logspan.log(s)
        span = etree.XML(s)
        parent_node.append(span)

    def update_xml(self):
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            val = nd_data['val']
            if tag in ['w', 'pc']:
                nd_id = nd_data['id']
                sp_data = self.span_data.get(nd_id, None)
                if sp_data is not None:
                    self.add_span(nd, sp_data)
                # elimina word vuote
                if val == '':
                    nd_p = nd.getparent()
                    nd_p.remove(nd)

    def add_span_to_root(self):
        try:
            self.root = etree.parse(self.src_path)
        except Exception as e:
            logerr.log("ERROR teimspan.py add_span_to_root")
            logerr.log(str(e))
            sys.exit(1)
        #
        self.row_tag_lst = ROW_LST
        for i in range (0,len(self.row_tag_lst)):
            self.set_js(i)
            self.span_data = {}
            self.from_id_open = ''
            self.fill_span()
            self.update_xml()
        #
        xml = etree.tostring(self.root,
                             xml_declaration=None,
                             encoding='unicode',
                             method="xml",
                             pretty_print=False,
                             with_tail=True,
                             standalone=None,
                             doctype=None,
                             exclusive=False,
                             inclusive_ns_prefixes=None,
                             strip_text=False)
        #
        # rimuove da xml tutti i pattern
        for x in self.op_lst:
            xml = xml.replace(x, '')
        for x in self.cl_lst:
            xml = xml.replace(x, '')
        with open(self.out_path, "w") as f:
            # TODO rimossa dichiarazionexml_decl = "<?xml version='1.0' encoding='utf-8' standalone='yes'?>"
            # f.write(xml_decl)
            f.write(xml)


def do_main(src_path, out_path):
    Addspan(src_path, out_path).add_span_to_root()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    try:
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
    except Exception as e:
        logerr.log("ERROR args in teimspan.py ")
        logerr.log(str(e))
        sys.exit(1)
    do_main(args.src, args.out)
