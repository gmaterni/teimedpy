#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import argparse
from lxml import etree

__date__ = "30-07-2018"
__version__ = "0.2.0"
__author__ = "Marta Materni"


def do_main(path_xml, path_out):
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
        print("ERROR XML")
        print(s)
        err_path = path_out.replace('.xml', '_err.log')
        with open(err_path, "w+") as fo:
            fo.write(s)


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
