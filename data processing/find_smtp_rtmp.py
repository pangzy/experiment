#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

list_dir = os.listdir(os.getcwd())

for item in list_dir:
    if os.path.isfile(item) and ".pcap" in item:
        print "processing\t" + item
        cmd1 = 'tshark -r'+' '+item+' '+'-V -Y "smtp" -n >'+' '+'smtp.txt'
        cmd2 = 'tshark -r'+' '+item+' '+'-V -Y "rtmp" -n >'+' '+'rtmp.txt'
        os.system(cmd1)
        os.system(cmd2)

print "finish all."
