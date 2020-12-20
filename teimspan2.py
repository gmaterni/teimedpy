#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aggiunge span from=.. to=..

dicorso diretto:  {}
monologo: {_}
la parentesi chiusa  può stare rispetto all'ultima patola o punto:
}word
word}
word }
.}
. }

agglutinazione:  []
agglutinazione incerta: [_]


"""
from lxml import etree
import os
import argparse
import sys
from teimed.teimlog import Log

__date__ = "09-11-2020"
__version__ = "0.210"
__author__ = "Marta Materni"


loginfo = Log()
logerr = Log()

OPDD = '{'  # dicorso diretto
OPMON = '{_'  # monologo
CLDM = '}'  # chiusra discorso direto / monologo

AGGLS = '['   # agglutinazione semplice rimozioni blank
AGGLU = '[_'  # aggltinazione  uncerts sostituzione blank  => -
CLAGG = ']'   # chiusra agglutinazione


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
        path_info = out_path.replace('.xml', '_span.log')
        path_err = out_path.replace('.xml', '_span_err.log')
        loginfo.open(path_info, out=0)
        logerr.open(path_err, out=1)

    # estra tag span dal sorgente xml
    # aggiunge un elemento a span_data
    # setta il corrispondenet from_id_actirve
    def span_from_src_xml(self, nd_data, tp):
        from_id = nd_data['id']
        item = {}
        item[DATA_TYPE] = tp
        item[DATA_TO] = ''
        item[DATA_FROM] = from_id
        key_data = from_id
        self.span_data[key_data] = item
        self.from_id_active = from_id

    # setta to_id in span_data utilizzando from_id_active
    def set_id_to_span_data(self, nd_data):
        try:
            to_id = nd_data['id']
            key_data = self.from_id_active
            item = self.span_data.get(key_data)
            item[DATA_TO] = to_id
        except Exception as e:
            loginfo.log("ERROR! teimspan set_id_to_span_data()")
            logerr.log("ERROR! teimspan set_id_to_span_data()")
            logerr.log(str(e))
            d = nd_data
            s = '{:<10} {:<10} {}'.format(d['id'], d['tag'], d['val'])
            loginfo.log(s)
            logerr.log(s)
            sys.exit(0)

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

    def write_span_log(self, oc, nd):
        d = self.get_node_data(nd)
        tag = d['tag']
        if tag == 'w':
            s = '{:<3}{:<10} {}'.format(oc, d['id'], d['val'])
            s = s.replace(os.linesep, ' ', -1)
            loginfo.log(s)
            if oc == 'C':
                loginfo.log("")

    # popola self.span_data
    def fill_span_direct(self):
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                # monologo
                if val.find(OPMON) > -1:
                    # print(f"OPMON {tag}  {val}  {text}")
                    self.write_span_log('M', nd)
                    self.span_from_src_xml(nd_data, 'monologue')
                    continue
                # dicorso diretto
                if val.find(OPDD) > -1:
                    # print(f"OPDD {tag}  {val}  {text}")
                    self.write_span_log('D', nd)
                    self.span_from_src_xml(nd_data, 'directspeech')
                    continue
                if val.find(CLDM) > -1:
                    if text.strip() == CLDM:
                        # print(f"CLDMa {tag}  {val}  {text}")
                        self.write_span_log('C', nd)
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_id_to_span_data(nd_data)
                    else:
                        # print(f"CLDMb {tag}  {val}  {text}")
                        self.write_span_log('C', nd)
                        self.set_id_to_span_data(nd_data)
                    continue

    def fill_span_aggl(self):
        for nd in self.root.iter():
            nd_data = self.get_node_data(nd)
            tag = nd_data['tag']
            if tag in ['w']:
                text = nd_data['text']
                val = nd_data['val']
                # print(f"{tag}  {val}  {text}")
                # agglutination_uncert
                if val.find(AGGLU) > -1:
                    # print(f"AGGLU {tag}  {val}  {text}")
                    self.write_span_log('AU', nd)
                    self.span_from_src_xml(nd_data, 'agglutination_uncert')
                    continue
                # agglutination
                if val.find(AGGLS) > -1:
                    # print(f"AGGLS {tag}  {val}  {text}")
                    self.write_span_log('AS', nd)
                    self.span_from_src_xml(nd_data, 'agglutination')
                    continue
                if val.find(CLAGG) > -1:
                    if text.strip() == CLAGG:
                       #  print(f"CLAGGa {tag}  {val}  {text}")
                        self.write_span_log('CA', nd)
                        nd_prev = self.get_prev(nd)
                        nd_data = self.get_node_data(nd_prev)
                        self.set_id_to_span_data(nd_data)
                    else:
                        # print(f"CLAGGb {tag}  {val}  {text}")
                        self.write_span_log('CA', nd)
                        self.set_id_to_span_data(nd_data)
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
    def get_parent_div(self, node):
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
        parent_node = self.get_parent_div(nd)
        if parent_node is None:
            print("ERROR. parent node  <div>  Not Found.")
            sys.exit(0)
        #
        from_id = sp_active[ACTIVE_FROM]
        to_id = sp_active[ACTIVE_TO]
        tp = sp_active[ACTIVE_TYPE]
        s = f'<span from="{from_id}" to="{to_id}" type="{tp}" />'
        #
        loginfo.log(s)
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
                # non è stata creata perchè non esiste psan_data di key id
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
        #
        self.span_active = {}
        self.span_data = {}
        self.from_id_active = ''
        self.fill_span_direct()
        self.update_xml()
        #
        self.span_active = {}
        self.span_data = {}
        self.from_id_active = ''
        self.fill_span_aggl()
        self.update_xml()
        #
        xml = etree.tostring(self.root,
                             xml_declaration=None,
                             encoding='unicode')

        xml = xml.replace(OPMON, '').replace(OPDD, '').replace(CLDM, '')
        xml = xml.replace(AGGLU, '').replace(AGGLS, '').replace(CLAGG, '')
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
        sys.exit()
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
        sys.exit(0)
    do_main(args.src, args.out)