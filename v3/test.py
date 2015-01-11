#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import system
from lib import *
from csv import *

# load data
glbv = load_glbv()
glbv2 = []

rp = open(glbv["config_file"], "rb")
rf = reader(rp)
for i in rf:
    glbv2.append(i)
rp.close()

wp = open(glbv["config_file"], "wb")
wf = writer(wp)

start_row = {"0": 0, "1": 830, "2": 1647, "3": 2466, "4": 3307, "5": 4127, "6": 4968,
             "7": 5796,"8": 6640, "9": 8098, "10": 11074, "11": 13636, "12": 15328,
             "13": 16756, "14": 21327, "15": 24410, "16": 27408, "17": 30195, "18": 32476,
             "19": 33740, "20": 35900, "21": 36508, "22": 37037, "23": 38154}
end_row = {"0": 829, "1": 1646, "2": 2465, "3": 3306, "4": 4126, "5": 4967, "6": 5795,
           "7": 6639,"8": 8097, "9": 11073, "10": 13635, "11": 15327, "12": 16755,
           "13": 21326, "14": 24409, "15": 27407, "16": 30194, "17": 32475, "18": 33739,
           "19": 35899, "20": 36507, "21": 37036, "22": 38153, "23": 38240}


for i in xrange(24):  # 24 hours
    glbv2[21][1] = str(start_row[str(i)])
    glbv2[22][1] = str(start_row[str(i)])
    for j in xrange(10):  # accuracy
        for k in xrange(5):  # 5 round miss
            glbv2[9][1] = str((10-j)*10.0/10)
            glbv2[10][1] = "1.0"
            wf.writerow(glbv2)

    for q in xrange(10):
        for p in xrange(5):  # 5 round false
            glbv2[9][1] = "1.0"
            glbv2[10][1] = str((10-q)*10.0/10)
            wf.writerow(glbv2)
            wp.close()





# generate data

