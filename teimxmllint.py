#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import argparse
from lxml import etree
from ualog import Log

__date__ = "10-01-2021"
__version__ = "0.3.0"
__author__ = "Marta Materni"

logerr = Log("w")

def do_main(path_xml, path_out):
    path_err = path_out.replace('.xml', '_ERR.log')
    logerr.open(path_err, out=1)
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.parse(path_xml, parser)
        src = etree.tostring(root,
                             method='xml',
                             xml_declaration=None,
                             encoding='unicode',
                             with_tail=True,
                             pretty_print=True)
        # s = etree.tostring(root, pretty_print=True)
        with open(path_out, "w+") as fw:
            fw.write(src)
        os.chmod(path_out, 0o666)
    except etree.Error as e:
        s = str(e)
        logerr.log("ERROR XML")
        logerr.log(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument('-i', dest="src", required=True, metavar="", help="-i <file input>")
    parser.add_argument('-o', dest="out", required=True, metavar="", help="-o <file output>")
    args = parser.parse_args()
    if args.src == args.out:
        print("Name File output errato")
        sys.exit(0)
    do_main(args.src, args.out)
