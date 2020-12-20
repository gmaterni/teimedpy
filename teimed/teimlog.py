#!/usr/bin/env python3
# coding: utf-8
# import datetime
import os

"""
print è attivato quando self.out+prn > 1
out.==1  prn== 1 attivato
out == 0 prn==1 NON attivato
out == 0 prn==2 attivato
"""


class Log(object):

    def __init__(self):
        self.used = False
        self.path_log =None
        self.out = None
        self.f = None


    def open (self, path_log, out=1):
        # ymd = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        # ymd = str(datetime.datetime.today().strftime('%Y%m%d_%H_%M'))
        # self.path_log = path_log.replace('.log', f'_{ymd}.log')
        self.path_log = path_log
        self.out = out
        self.f = None

    def log(self, s, prn=1):
        if self.used is False:
            self.used = True
            self.f = open(self.path_log, "w")
            os.chmod(self.path_log, 0o666)
        self.f.write(s)
        self.f.write(os.linesep)
        self.f.flush()
        if self.out + prn > 1:
            print(s)
        return self
