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

pcap = pyshark.FileCapture(file_rd, display_filter="http.response and (not tcp.reassembled.data or tcp.reassembled.length < 1000000)", keep_packets=False)

lines = ""

for p in pcap:
    print file_rd
    print p.frame_info.number
    try:
        if int(p.http.content_length) > 0:
            lines = lines + p.http.request_in + "\t" + p.http.content_length + "\t"
            try:
                lines = lines + p.http.content_type + "\n"
            except AttributeError as e2:
                lines = lines + "other" + "\n"
        else:
            pass
    except AttributeError as e1:
        pass

file_wrt = file_rd.split(".")[0]+"_response.txt"

wf = open(file_wrt, "w")
wf.writelines(lines)
wf.close()