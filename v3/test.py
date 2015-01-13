#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import system
from lib import *
from openpyxl import *

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

"""
for i in xrange(6):
    for j in xrange(5):  # accuracy
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B22").set_explicit_value(24410, data_type="n")  # 15:00
            ws.cell("B23").set_explicit_value(end_row2[str(i)], data_type="n")
            ws.cell("B10").set_explicit_value((10-j)/10.0, data_type="n")
            ws.cell("B11").set_explicit_value(1.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/pzy/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()

    for q in xrange(5):
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B22").set_explicit_value(24410, data_type="n")  # 15:00
            ws.cell("B23").set_explicit_value(end_row2[str(i)], data_type="n")
            ws.cell("B10").set_explicit_value(1.0, data_type="n")
            ws.cell("B11").set_explicit_value((10-q)/10.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/pzy/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()


for i in xrange(24):  # 24 hours
    for j in xrange(5):  # accuracy
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B22").set_explicit_value(0, data_type="n")  # 15:00
            ws.cell("B23").set_explicit_value(end_row[str(i)], data_type="n")
            ws.cell("B10").set_explicit_value((10-j)/10.0, data_type="n")
            ws.cell("B11").set_explicit_value(1.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/pzy/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()

    for q in xrange(5):
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B22").set_explicit_value(0, data_type="n")  # 15:00
            ws.cell("B23").set_explicit_value(end_row[str(i)], data_type="n")
            ws.cell("B10").set_explicit_value(1.0, data_type="n")
            ws.cell("B11").set_explicit_value((10-q)/10.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/pzy/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()
"""
# generate data
for i in xrange(6):
    for j in xrange(5):  # accuracy
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B12").set_explicit_value("g", data_type="s")  # maxs
            ws.cell("B14").set_explicit_value("poisson", data_type="s")  # maxs
            ws.cell("B2").set_explicit_value(600*(i+1), data_type="n")  # tn
            ws.cell("B4").set_explicit_value(10, data_type="n")  # f
            ws.cell("B8").set_explicit_value(204800, data_type="n")  # maxs
            ws.cell("B9").set_explicit_value(50, data_type="n")  # mins
            ws.cell("B10").set_explicit_value((10-j)/10.0, data_type="n")
            ws.cell("B11").set_explicit_value(1.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/test_1/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()

    for q in xrange(5):
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B12").set_explicit_value("g", data_type="s")  # maxs
            ws.cell("B14").set_explicit_value("poisson", data_type="s")  # maxs
            ws.cell("B2").set_explicit_value(600*(i+1), data_type="n")  # tn
            ws.cell("B4").set_explicit_value(10, data_type="n")  # f
            ws.cell("B8").set_explicit_value(204800, data_type="n")  # maxs
            ws.cell("B9").set_explicit_value(50, data_type="n")  # mins
            ws.cell("B10").set_explicit_value(1.0, data_type="n")
            ws.cell("B11").set_explicit_value((10-q)/10.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/test_1/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()


for i in xrange(24):  # 24 hours
    for j in xrange(5):  # accuracy
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B12").set_explicit_value("g", data_type="s")  # maxs
            ws.cell("B14").set_explicit_value("poisson", data_type="s")  # maxs
            ws.cell("B2").set_explicit_value(3600*(i+1), data_type="n")  # tn
            ws.cell("B4").set_explicit_value(10, data_type="n")  # f
            ws.cell("B8").set_explicit_value(204800, data_type="n")  # maxs
            ws.cell("B9").set_explicit_value(50, data_type="n")  # mins
            ws.cell("B10").set_explicit_value((10-j)/10.0, data_type="n")
            ws.cell("B11").set_explicit_value(1.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/test_1/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()

    for q in xrange(5):
        try:
            wb = load_workbook(glbv["config_file"])
            ws = wb.get_sheet_by_name("Sheet1")
            ws.cell("B12").set_explicit_value("g", data_type="s")  # maxs
            ws.cell("B14").set_explicit_value("poisson", data_type="s")  # maxs
            ws.cell("B2").set_explicit_value(3600*(i+1), data_type="n")  # tn
            ws.cell("B4").set_explicit_value(10, data_type="n")  # f
            ws.cell("B8").set_explicit_value(204800, data_type="n")  # maxs
            ws.cell("B9").set_explicit_value(50, data_type="n")  # mins
            ws.cell("B10").set_explicit_value(1.0, data_type="n")
            ws.cell("B11").set_explicit_value((10-q)/10.0, data_type="n")
            wb.save(glbv["config_file"])
            system("python /home/pangzy/virtualenv/test_1/test/simulation.py")
            # system("simulation.py")
            # pause()
        except KeyboardInterrupt:
            print "\nCaught KeyboardInterrupt, program terminate."
            exit()