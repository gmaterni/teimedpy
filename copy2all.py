#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pathlib as pl


"""
 copia i files json di un manoscritto inaltri manoscritti

 copy2all.py dir man man1 man2 man3 ..
 dir:dir dei manoscritti
 man: manoscritto sorgentr
 man1 man2 ..:manoscritti destinazione

"""
def files_of_dir(d, e):
    p = pl.Path(d)
    fs = sorted(list(p.glob(e)))
    return fs

def copy_man(orig_path,man_path,orig,man):
    with open(orig_path,"r") as f:
        txt=f.read()
    txt=txt.replace(orig,man)
    print(f"{orig_path} ==> {man_path}")
    with open(man_path,"w") as f:
        f.write(txt)
    os.chmod(man_path,0o666)

def one2all(dr,orig,*args):
    man_lst=args[0]
    ptrn=f'{orig}*.*'
    orig_lst=files_of_dir(dr,ptrn)
    for orig_path in orig_lst:
        orig_path=str(orig_path)
        for man in man_lst:
            path_man=orig_path.replace(orig,man)
            copy_man(orig_path,path_man,orig,man)


if __name__ == "__main__":
    if len(sys.argv)==1:
        print(f"copy2all.py <dir> <sigla sorgente> <sigla1> <sigla2> ..")
        sys.exit(0)
    dr=sys.argv[1]
    man=sys.argv[2]
    mans=sys.argv[3:]
    man_ls=[x for x in mans]
    one2all(dr,man,man_ls)