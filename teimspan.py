#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggiunge span from=.. to=..

dicorso diretto:  {}
monologo: {_}

la parentesi chiusa può stare rispetto all'ultima patola
 o punto:

}word
word}
word }
.}
. }


agglutinazione:  []
agglutinazione incerta: [_]

damage: %0  0%

"""
from pdb import set_trace
from lxml import etree
import os
import argparse
import sys
from ualog import Log

__date__ = "14-01-2021"
__version__ = "0.9.2"
__author__ = "Marta Materni"


logspan = Log('w')
logerr = Log('w')

ODD = '{'    # dicorso diretto
OMO = '{_'  # monologo
CDM = '}'    # chiusra discorso direto / monologo
LODD = 'ODRD '
LOMO = 'ODMON'
LCDM = 'CDRMO'

OAGLS = '['    # agglutinazione semplice rimozioni blank
OAGLU = '[_'   # aggltinazione  uncerts sostituzione blank  => -
CAGL = ']'    # chiusra agglutinazione
LOAGLS = 'OAGGLS'
LOAGLU = 'OAGGLU'
LCAGL = 'CAGGL '

ODAM = '%0'  # damage
CDAM = '0%'  # damage
LODAM = 'ODAMG'
LCDAM = 'CDAMG'


DATA_TYPE = "tp"
DATA_FROM = "from"
DATA_TO = "to"

ACTIVE_TYPE = 'tp'
ACTIVE_FROM = 'from'
ACTIVE_TO = 'to'


class Addspan(object):

    def __init__(self, src_path, out_path):
        self.src_path = src_path
        self.out_path = out_path
        self.root = None
        self.span_data = None
        self.span_active = None
        self.from_id_active = ''
        self.ctrl_direct=0
        self.ctrl_agglut=0
        self.ctrl_damage=0
        path_span = out_path.replace('.xml', '_span.log')
        path_err = out_path.replace('.xml', '_span')
        logspan.open(path_span, out=0)
        logerr.open(path_err, out=1)


    # estra tag span dal sorgente xml
    # aggiunge un elemento a span_data
    # setta il corrispondenet from_id_actirve
    def set_from_id(self, nd_data, tp):
        from_id = nd_data['id']
        item = {}
        item[DATA_TYPE] = tp
        item[DATA_TO] = ''
        item[DATA_FROM] = from_id
        key_data = from_id
        self.span_data[key_data] = item
        self.from_id_active = from_id
        return from_id

    # setta to_id in span_data utilizzando from_id_active
    def set_to_id(self, nd_data):
        try:
            to_id = nd_data['id']
            key_data = self.from_id_active
            item = self.span_data.get(key_data)
            item[DATA_TO] = to_id
            return to_id
        except Exception as e:
            logerr.log("ERROR ! teimspan set_id_to()")
            logerr.log(str(e))
            d = nd_data
            s = '{:<10} {:<10} {}'.format(d['id'], d['tag'], d['val'])
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


    def control_from_to(self,oc):
        if oc==LODD or oc ==LOMO:
            self.ctrl_direct+=1
            if self.ctrl_direct > 2:
                logspan.log(" ERROR  missing {CDM}")
                logspan.log("")
                self.ctrl_direct-=1
        elif oc==LCDM:
            self.ctrl_direct-=1
            if self.ctrl_direct < 0:
                logspan.log(f" ERROR  missing {ODD} or {OMO}")
                self.ctrl_direct+=1
        elif oc==LOAGLS or oc==LOAGLU:
            self.ctrl_agglut+=1
            if self.ctrl_agglut > 2:
                logspan.log(f" ERROR missing {CAGL}")
                logspan.log("")
                self.ctrl_agglut-=1
        elif oc==LCAGL:
            self.ctrl_agglut-=1
            if self.ctrl_agglut < 0:
                logspan.log(f" ERROR  missing {OAGLS} or {OAGLU}")
                self.ctrl_agglut+=1
        elif oc==LODAM:
            self.ctrl_damage+=1
            if self.ctrl_damage > 2:
                logspan.log(f" ERROR missing {CDAM}")
                logspan.log("")
                self.ctrl_damage-=1
        elif oc==LCDAM:
            self.ctrl_damage-=1
            if self.ctrl_damage <0:
                logspan.log(f" ERROR missing {ODAM}")
                self.ctrl_damage +=1


    def write_span_log(self, oc, nd, ft):
        d = self.get_node_data(nd)
        self.control_from_to(oc)
        if ft =='f':
            ft_id = f"from:{d['id']}"
        else:
            ft_id = f"to  :{d['id']}"
        s = '{:<9} {:<25} {}'.format(oc, ft_id, d['val'])
        s = s.replace(os.linesep, ' ', -1)
        logspan.log(s)
        if oc[0] == 'C':
            logspan.log("")

    # popola self.span_data
    def fill_span_direct_monolog(self):
        logspan.log("Controllo direct./monolog"+os.linesep)
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                # monologo
                if val.find(OMO) > -1:
                    # print(f{LOMO}{tag}  {val}  {text}")
                    self.set_from_id(nd_data, 'monologue')
                    self.write_span_log(LOMO, nd, 'f')
                    continue
                # dicorso diretto
                if val.find(ODD) > -1:
                    # print(f"{LODD} {tag}  {val}  {text}")
                    self.set_from_id(nd_data, 'directspeech')
                    self.write_span_log(LODD, nd,'f')
                    continue
                if val.find(CDM) > -1:
                    if text.strip() == CDM:
                        # print(f{LCDM}_A {tag}  {val}  {text}")
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_to_id(nd_data)
                        self.write_span_log(LCDM, nd, 't')
                    else:
                        # print(f"{LCDN}_B {tag}  {val}  {text}")
                        self.set_to_id(nd_data)
                        self.write_span_log(LCDM, nd, 't')
                    continue

    def fill_span_aggl(self):
        logspan.log(os.linesep+"Controllo agglutination"+os.linesep)
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                # print(f"{tag}  {val}  {text}")
                # agglutination_uncert
                if val.find(OAGLU) > -1:
                    # print(f"{LOAGLU} {tag}  {val}  {text}")
                    self.set_from_id(nd_data, 'agglutination_uncert')
                    self.write_span_log(LOAGLU, nd, 'f')
                    continue
                # agglutination
                if val.find(OAGLS) > -1:
                    # print(f"{LOAGLS} {tag}  {val}  {text}")
                    self.set_from_id(nd_data, 'agglutination')
                    self.write_span_log(LOAGLS, nd,'f')
                    continue
                if val.find(CAGL) > -1:
                    if text.strip() == CAGL:
                        # print(f"{LCAGL}_A {tag}  {val}  {text}{os.linesep}")
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_to_id(nd_data)
                        self.write_span_log(LCAGL, nd,'t')
                    else:
                        # print(f"{LCAGL}_B {tag}  {val}  {text}{os.linesep}")
                        self.set_to_id(nd_data)
                        self.write_span_log(LCAGL, nd, 't')
                    continue

    def fill_span_damage(self):
        logspan.log(os.linesep+"Controllo damage"+os.linesep)
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                # print(f"{tag}  {val}  {text}")
                # damage
                if val.find(ODAM) > -1:
                    # print(f"{LODAM} {tag}  {val}  {text}")
                    self.set_from_id(nd_data, 'damage')
                    self.write_span_log(LODAM, nd,'f')
                    continue
                if val.find(CDAM) > -1:
                    if text.strip() == CDAM:
                        # print(f"{LCDAM}_A {tag}  {val}  {text}{os.linesep}")
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_to_id(nd_data)
                        self.write_span_log(LCDAM, nd,'t')
                    else:
                        # print(f"{LCDAM}_B {tag}  {val}  {text}{os.linesep}")
                        self.set_to_id(nd_data)
                        self.write_span_log(LCDAM, nd, 't')
                    continue

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

    # se esiste in span_data crea un item in span_active
    # e ritoena True
    # altrimenti ritoena False
    # la key di span_data è from_id
    #
    # <to_id>:{'from':<from_id>,'to':<to_id>,'type':<'tipo'>}
    #
    def create_span_active(self, key_data):
        sp_data = self.span_data.get(key_data, None)
        if sp_data is None:
            return False
        item = {}
        item[ACTIVE_FROM] = sp_data[DATA_FROM]
        item[ACTIVE_TO] = sp_data[DATA_TO]
        item[ACTIVE_TYPE] = sp_data[DATA_TYPE]
        key_active = sp_data[DATA_TO]
        self.span_active[key_active] = item
        return True

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

    def add_span(self, nd, sp_active):
        parent_node = self.get_span_parent(nd)
        if parent_node is None:
            logerr.log("ERROR. parent node <div>  Not Found.")
            sys.exit(1)
        #
        from_id = sp_active[ACTIVE_FROM]
        to_id = sp_active[ACTIVE_TO]
        tp = sp_active[ACTIVE_TYPE]
        s = f'<span from="{from_id}" to="{to_id}" type="{tp}" />'
        # TODO 
        # logspan.log(s)
        span = etree.XML(s)
        parent_node.append(span)

    def update_xml(self):
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            val = nd_data['val']
            if tag in ['w', 'pc']:
                # controlla vid in span_data, se esistea crea un span_active
                vid = nd_data['id']
                id_in_nd_data = self.create_span_active(vid)
                # non è stata creata perchè non esiste span_data di key id
                if not id_in_nd_data:
                    sp_active = self.span_active.get(vid, None)
                    if sp_active is not None:
                        self.add_span(nd, sp_active)
                # elimina word vuote
                if val == '':
                    nd_p = nd.getparent()
                    nd_p.remove(nd)

    def add_span_to_root(self):
        self.root = etree.parse(self.src_path)
        # direct /monologue
        self.span_active = {}
        self.span_data = {}
        self.from_id_active = ''
        self.fill_span_direct_monolog()
        self.update_xml()
        # agglutination
        self.span_active = {}
        self.span_data = {}
        self.from_id_active = ''
        self.fill_span_aggl()
        self.update_xml()
        # damage
        self.span_active = {}
        self.span_data = {}
        self.from_id_active = ''
        self.fill_span_damage()
        self.update_xml()
        #
        xml = etree.tostring(self.root,
                             xml_declaration=None,
                             encoding='unicode')
        xml = xml.replace(OMO, '').replace(ODD, '').replace(CDM, '')
        xml = xml.replace(OAGLU, '').replace(OAGLS, '').replace(CAGL, '')
        xml = xml.replace(ODAM, '').replace(CDAM, '')
        #
        with open(self.out_path, "w+") as f:
            xml_decl = "<?xml version='1.0' encoding='utf-8' standalone='yes'?>"
            f.write(xml_decl)
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
        if args.src == args.out:
            print("Nome File output errato")
            sys.exit(1)
    except Exception as e:
        logerr.log("ERROR args in teimspan ")
        logerr.log(str(e))
        sys.exit(1)
    do_main(args.src, args.out)
