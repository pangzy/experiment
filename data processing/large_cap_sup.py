#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def pause():
    if raw_input("press any key to continue:"):
        pass

list_dir = os.listdir(os.getcwd())

for line in list_dir:
    if os.path.isfile(line) and ".pcap" in line:
        print "processing\t" + line
        cmd1 = 'tshark -r'+' '+line+' '+'-V -Y "http.response and mp4 and http.request_in" -n -T fields ' + \
               '-e http.request_in -e http.content_length -e http.content_type >' + ' ' + \
               line.split(".")[0]+'_sup_mp4.txt'
        os.system(cmd1)

        cmd2 = 'tshark -r'+' '+line+' '+'-V -Y "http.response and tcp.reassembled.length > 1000000 and http.request_in" -n -T fields ' + \
               '-e http.request_in -e http.content_length -e http.content_type >' + ' ' + \
               line.split(".")[0]+'_sup_length.txt'
        os.system(cmd2)