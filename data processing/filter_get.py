#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyshark
import sys

reload(sys)
sys.setdefaultencoding("utf8")


def pause():
    if raw_input("press any key to continue:"):
        pass

file_rd = sys.argv[1]

pcap = pyshark.FileCapture(file_rd, display_filter="http.request.method == GET", keep_packets=False)

lines = ""

for p in pcap:
    try:
        lines = lines + p.frame_info.number + "\t" + str(p.sniff_time) + "\t" + p.eth.src + "\n"
    except AttributeError as e:
        pass

file_wrt = file_rd.split(".")[0]+"_get.txt"

wf = open(file_wrt, "w")
wf.writelines(lines)
wf.close()