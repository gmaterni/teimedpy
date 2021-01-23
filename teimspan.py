#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggiunge span from=.. to=..
es. tag from to

TYPE|TAG_FROM|TAG_TO|SIGLA_FROM!SIGLA_TO
directspeech|{|}|ODRD|CDRD
monologue|{_|_}|OMON|CMON
agglutination|[|]|OAGLS|CAGLS
agglutination_uncert|[_|_]|OAGLU|CAGLU
damage|{0%|%0}|ODAM|CDAM
damagel_low|{1%|%1}|ODAML|CDAML
damage_medium|{2%|%2}|ODAMM|CDAMM
damage_high|{3%|%3}|ODAMH|CDAMH
"""
from pdb import set_trace
from lxml import etree
import os
import argparse
import sys
from ualog import Log
import pprint
import re

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
        self.key_span_data = ''
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
        op = row[1]       # tag opne
        cl = row[2]       #  tag close
        # nella lista di controllo son settati i tag di lunghezza
        # > del tag selezionato
        for j, r in enumerate(self.row_tag_lst):
            o=r[1]
            c=r[2]
            self.op_lst.append(o)
            self.cl_lst.append(c)
            if j == i:
                continue
            if len(o) > len(op) :
                self.op_alter.append(o)
            if len(c) > len(cl) :
                self.cl_alter.append(c)

    def node_liv(self, node):
        d = 0
        while node is not None:
            d += 1
            node = node.getparent()
        return d - 1

    def node_tag(self, nd):
        tag = nd.tag
        tag = tag if type(nd.tag) is str else "XXX"
        p = tag.rfind('}')
        if p > 1:
            logerr.log(os.linesep+"ERROR teimspan node_tag()")
            logerr.log(tag)
            sys.exyt(1)
        return tag.strip()

    def node_id(self, nd):
        s = ''
        kvs = nd.items()
        for kv in kvs:
            if kv[0].rfind('id') > -1:
                s = kv[1]
                break
        return s

    def node_text(self, nd):
        text = nd.text
        text = '' if text is None else text.strip()
        text = text.strip().replace(os.linesep, ',,')
        return text


    def node_tail(self, nd):
        tail = '' if nd.tail is None else nd.tail
        tail = tail.strip().replace(os.linesep, '')
        return tail

    def node_val(self, nd):
        """
        ls = []
        for x in nd.itertext():
            ls.append(x)
        text = " ".join(ls)
        return text
        """
        val = ""
        for t in nd.itertext():
            val = val + t
        return val

    def get_node_data(self, nd):
        tag=self.node_tag(nd)
        id=self.node_id(nd)
        text=self.node_text(nd)
        val=self.node_val(nd)
        tail=self.node_tail(nd)
        liv=self.node_liv(nd)
        nd_data = {
            'tag': tag.strip(),
            'id': id,
            'text': text,
            'val': val,
            'tail':tail,
            'liv':liv
        }
        return nd_data

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
        self.key_span_data = from_id

    # setta to_id in span_data utilizzando from_id_open
    def set_to_id(self, nd_data):
        try:
            if self.key_span_data is None:
                return                
            if nd_data is None:\
                raise Exception(f"nd_data is nill")
            to_id = nd_data['id']
            item = self.span_data.get(self.key_span_data, None)
            if item is None:
                raise Exception(f"key_span:{self.key_span_data} Not Found.")
            item[DATA_TO] = to_id
        except Exception as e:
            logerr.log(os.linesep+"ERROR teimspan set_id_to()")
            logerr.log(f'TYPE:{self.js[TP]}')
            logerr.log(str(e)+os.linesep)
            logspan.log(str(e)+os.linesep)
            sys.exit(1)

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

    def control_open(self,nd):
        self.js[CTRL] += 1
        if self.js[CTRL] > 1:
            log_cl = self.js[LCL]
            xml = self.xml2str(nd).strip()
            e=f"** ERROR missing {log_cl}"
            s = '{:<30}{}'.format(e,xml)
            logspan.log(s)
            logspan.log("")
            self.js[CTRL] -= 1
            logerr.log(s)
    
    def control_close(self,nd):
        self.js[CTRL] -= 1
        if self.js[CTRL] < 0:
            log_op = self.js[LOP]
            xml = self.xml2str(nd).strip()
            e=f"** ERROR missing {log_op}"
            s = '{:<30}{}'.format(e,xml)
            logspan.log(s)
            self.js[CTRL] += 1
            logerr.log(s)

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
    ATTNZIONE
        in chiusura la ricerca avviene a partire da destra
        utilizzanod re group.end()
    
    """
    def find_tag_from(self, s):
        t = self.js[OP]
        p0 = s.find(t)
        if p0 < 0:
            return False
        ok = True
        for x in self.op_alter:
            p1=s.find(x) 
            if p1 > -1 and p0==p1:
                return False
        return ok

    def find_tag_to(self, s):
        t = self.js[CL]
        m=re.search(t,s)
        if m is None:
            return False
        p0=m.end()
        ok = True
        for x in self.cl_alter:
            m=re.search(x,s)
            p1=-1 if m is None else m.end()
            if p1 > -1 and p0==p1 :
                return  False
        return ok


    def fill_span(self):
        tp = self.js[TP]
        logspan.log(f">>>     {tp}     <<<"+os.linesep)
        for nd in self.root.iter():
            trace=False
            # esclude iltag body(liv 0)
            tag=self.node_tag(nd)
            if tag == 'body':
                continue
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            #########
            """
            id=nd_data.get('id','XXX')
            if id=='Gl1w2':
                trace=True
                set_trace()
                pass
            """
            ########
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                #
                if self.find_tag_from(val):
                    # print(f"{self.js[LOP]} {self.js[OP]}  {val} {text}")
                    self.set_from_id(nd_data)
                    self.control_open(nd)
                    self.log_open(nd)
                #
                if self.find_tag_to(val):
                    if text.strip() == self.js[CL]:
                        # print(f"{self.js[OP]}_A {self.js[OP]}  {val} {text}")
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_to_id(nd_data)
                        self.control_close(nd)
                        self.log_close(nd)
                    else:
                        # print(f"{self.js[LOP]}_B {self.js[OP]}  {val} {text}")
                        self.set_to_id(nd_data)
                        self.control_close(nd)
                        self.log_close(nd)

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
            # esclude iltag body(liv 0)
            tag=self.node_tag(nd)
            if tag == 'body':
                continue
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w', 'pc']:
                nd_id = nd_data['id']
                sp_data = self.span_data.get(nd_id, None)
                if sp_data is not None:
                    self.add_span(nd, sp_data)
                # elimina word vuote
                val = nd_data['val']
                if val == '':
                    nd_p = nd.getparent()
                    nd_p.remove(nd)


    def read_tag_from_to(self, csv_path):
        try:
            with open(csv_path, "r") as f:
                txt = f.read()  
            #txt=txt.replace(f'\{os.linesep}','')
            csv=txt.split(os.linesep)
            csv_rows=[]
            for row in csv:
                row=row.strip()
                if row == "":
                    continue
                row = row.replace(os.linesep, '')    
                row = row.replace(' ', '')
                flds = row.split('|')
                x = flds[0]
                if x.lower() == 'type':
                    continue
                csv_rows.append(flds)
            return csv_rows
        except Exception as e:
            logerr.log("ERROR teimspan.py read csv")
            logerr.log(str(e))
            sys.exit(1)

    
    def add_span_to_root(self,csv_path):
        try:
            self.root = etree.parse(self.src_path)
        except Exception as e:
            logerr.log(os.linesep+"ERROR teimspan.py add_span_to_root()")
            logerr.log(str(e))
            sys.exit(1)
        #
        self.row_tag_lst = self.read_tag_from_to(csv_path)
        for i in range (0,len(self.row_tag_lst)):
            self.set_js(i)
            self.span_data = {}
            self.key_span_data = None
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
            # f.write(xml_decl)
            f.write(xml)


def do_main(src_path, out_path, csv_path):
    Addspan(src_path, out_path).add_span_to_root(csv_path)


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
        parser.add_argument('-c',
                            dest="cfg",
                            required=True,
                            metavar="",
                            help="-c <file csv dei tag>")
        args = parser.parse_args()
    except Exception as e:
        logerr.log("ERROR args in teimspan.py ")
        logerr.log(str(e))
        sys.exit(1)
    do_main(args.src, args.out,args.cfg)
