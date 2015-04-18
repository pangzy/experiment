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
rd_sup_mp4 = prefix + "_sup_mp4.txt"
rd_sup_length = prefix + "_sup_length.txt"

w_lines1 = ""
w_lines2 = ""

f1 = open(rd_sup_mp4)
f2 = open(rd_sup_length)
f0 = open(rd_get)

lines1 = f1.readlines()
lines2 = f2.readlines()
lines0 = f0.readlines()

tmp_lines1 = []
tmp_lines2 = []
tmp_lines0 = []

for line1 in lines1:
    ls1 = line1.split()
    request_in = int(ls1[0])
    content_length = ls1[1]
    content_type = ls1[2]
    tmp_lines1.append([request_in, content_length, content_type])

for line2 in lines2:
    ls2 = line2.split()
    request_in = int(ls2[0])
    content_length = ls2[1]
    content_type = ls2[2]
    tmp_lines2.append([request_in, content_length, content_type])

for line0 in lines0:
    ls0 = line0.split()
    frame_number = int(ls0[0])
    t = ls0[1]+" "+ls0[2][:-7]
    mac = ls0[3]
    tmp_lines0.append([frame_number, t, mac])

tmp_lines1 = sorted(tmp_lines1, key=itemgetter(0))
tmp_lines2 = sorted(tmp_lines2, key=itemgetter(0))
tmp_lines0 = sorted(tmp_lines0, key=itemgetter(0))

request_count = 0
for line1 in tmp_lines1:
    request_in = line1[0]
    content_length = line1[1]
    content_type = line1[2]
    for i in xrange(request_count, len(tmp_lines0)):
        frame_number = tmp_lines0[i][0]
        t = tmp_lines0[i][1]
        mac = tmp_lines0[i][2]
        if frame_number == request_in:
            w_lines1 = w_lines1 + t + "\t" + mac + "\t" + content_length + "\t" + content_type + "\n"
            request_count = i+1
            break

request_count = 0
for line2 in tmp_lines2:
    request_in = line2[0]
    content_length = line2[1]
    content_type = line2[2]
    for i in xrange(request_count, len(tmp_lines0)):
        frame_number = tmp_lines0[i][0]
        t = tmp_lines0[i][1]
        mac = tmp_lines0[i][2]
        if frame_number == request_in:
            w_lines2 = w_lines2 + t + "\t" + mac + "\t" + content_length + "\t" + content_type + "\n"
            request_count = i+1
            break

file1_wrt = prefix + "_sup_mp4.dat"
file2_wrt = prefix + "_sup_length.dat"

wf1 = open(file1_wrt, "w")
wf1.writelines(w_lines1)
wf1.close()

wf2 = open(file2_wrt, "w")
wf2.writelines(w_lines2)
wf2.close()