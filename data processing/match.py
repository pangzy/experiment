#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from operator import itemgetter


def pause():
    if raw_input("press any key to continue:"):
        pass

file_rd = sys.argv[1]

prefix = file_rd.split(".")[0]

rd_get = prefix + "_get.txt"
rd_response = prefix + "_response.txt"

f1 = open(rd_response)
f2 = open(rd_get)

w_lines = ""
lines1 = f1.readlines()
lines2 = f2.readlines()

tmp_lines1 = []
tmp_lines2 = []

for line1 in lines1:
    ls1 = line1.split()
    request_in = int(ls1[0])
    content_length = ls1[1]
    content_type = ls1[2]
    tmp_lines1.append([request_in, content_length, content_type])

for line2 in lines2:
    ls2 = line2.split()
    frame_number = int(ls2[0])
    t = ls2[1]+" "+ls2[2][:-7]
    mac = ls2[3]
    tmp_lines2.append([frame_number, t, mac])

tmp_lines1 = sorted(tmp_lines1, key=itemgetter(0))
tmp_lines2 = sorted(tmp_lines2, key=itemgetter(0))

request_count = 0
for line1 in tmp_lines1:
    request_in = line1[0]
    content_length = line1[1]
    content_type = line1[2]
    for i in xrange(request_count, len(tmp_lines2)):
        frame_number = tmp_lines2[i][0]
        t = tmp_lines2[i][1]
        mac = tmp_lines2[i][2]
        if frame_number == request_in:
            w_lines = w_lines + t + "\t" + mac + "\t" + content_length + "\t" + content_type + "\n"
            request_count = i+1
            break

file_wrt = prefix + ".dat"

wf = open(file_wrt, "w")
wf.writelines(w_lines)
wf.close()


'''

for line1 in lines1:
    ls1 = line1.split()
    request_in = int(ls1[0])
    content_length = ls1[1]
    content_type = ls1[2]

    for line2 in lines2:
        ls2 = line2.split()
        frame_number = int(ls2[0])
        t = ls2[1]+" "+ls2[2][:-7]
        mac = ls2[3]
        if frame_number == request_in:
            #print i
            # pause()
            w_lines = w_lines + t + "\t" + mac + "\t" + content_length + "\t" + content_type + "\n"
            break
'''