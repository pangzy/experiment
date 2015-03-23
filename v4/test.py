#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import system
from lib import *
from openpyxl import *
from ConfigParser import ConfigParser

# load data
glbv = load_glbv()

start_row = {"0": 0, "1": 830, "2": 1647, "3": 2466, "4": 3307, "5": 4127, "6": 4968,
             "7": 5796,"8": 6640, "9": 8098, "10": 11074, "11": 13636, "12": 15328,
             "13": 16756, "14": 21327, "15": 24410, "16": 27408, "17": 30195, "18": 32476,
             "19": 33740, "20": 35900, "21": 36508, "22": 37037, "23": 38154}

end_row = {"0": 829, "1": 1646, "2": 2465, "3": 3306, "4": 4126, "5": 4967, "6": 5795,
           "7": 6639,"8": 8097, "9": 11073, "10": 13635, "11": 15327, "12": 16755,
           "13": 21326, "14": 24409, "15": 27407, "16": 30194, "17": 32475, "18": 33739,
           "19": 35899, "20": 36507, "21": 37036, "22": 38153, "23": 38240}

end_row2 = {"0": 24983, "1": 25885, "2": 26237,"3": 26749,"4": 27032,"5": 27407}


for i in xrange(1):  # 24 hours
    for j in xrange(1):  # accuracy
        try:
            cf = ConfigParser()
            cf.read(glbv["config_file"])
            cf.set("glbv", "source", "g")
            cf.set("glbv", "dis", "poisson")
            cf.set("glbv", "tn", 600*(i+1))
            cf.write(open(glbv["config_file"],"w"))
            # system("python /home/pangzy/virtualenv/test_1/test/simulation.py")
            system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()