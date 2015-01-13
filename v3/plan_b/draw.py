#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from xlrd import *

def pause():
    if raw_input("press any key to continue:"):
        pass


def draw(data_file, scheme=0):

    rb = open_workbook(data_file)
    s1 = rb.sheet_by_index(1)  # perfect
    s2 = rb.sheet_by_index(2)  # imperfect
    s3 = rb.sheet_by_index(3)  # fcfs_perfect
    s4 = rb.sheet_by_index(4)  # fcfs_imperfect


    if scheme == 1:
        pr = []
        x = []
        y = []
        for i in xrange(1, s1.nrows):
            if s1.row(i)[9].value == 1 and s1.row(i)[10].value == 1:
                pr.append(s1.row_values(i))

        for r1 in pr:
            for r2 in pr[::-1]:
                if r2 != r1 and r2[1] == r1[1]:
                    pr.pop(pr.index(r2))

        for r in pr:
            x.append(r[1])
            y.append(r[11])

        plt.plot(x, y)
        plt.plot(x, y, "bo")
        plt.title("omega")
        plt.xlabel("omega")
        plt.ylabel("speed up")
        plt.show()

    if scheme == 2:
        x = [1, 0.9, 0.8, 0.7, 0.6]

        plt.figure(1)
        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+1].value)
        plt.subplot(231)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("600s", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+11].value)
        plt.subplot(232)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("1200s", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+21].value)
        plt.subplot(233)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("1800s", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+31].value)
        plt.subplot(234)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("2400s", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+41].value)
        plt.subplot(235)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("3000s", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+51].value)
        plt.subplot(236)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("3600s", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        plt.show()

    if scheme == 3:
        x = [1, 0.9, 0.8, 0.7, 0.6]
        plt.figure(1)

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+6].value)
        plt.subplot(231)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("600s", fontsize=10)
        plt.xlabel("precision", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+16].value)
        plt.subplot(232)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("1200s", fontsize=10)
        plt.xlabel("precision", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+26].value)
        plt.subplot(233)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("1800s", fontsize=10)
        plt.xlabel("precision", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+36].value)
        plt.subplot(234)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("2400s", fontsize=10)
        plt.xlabel("precision", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+46].value)
        plt.subplot(235)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("3000s", fontsize=10)
        plt.xlabel("precision", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+56].value)
        plt.subplot(236)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("3600s", fontsize=10)
        plt.xlabel("precision", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        plt.show()

    if scheme == 4:
        x = [600, 1200, 1800, 2400, 3000, 3600, 7200]

        plt.figure(1)
        plt.xlabel("omega")
        plt.ylabel("speed up (%)")
        y = [s2.col(12)[1].value, s2.col(12)[11].value, s2.col(12)[21].value, s2.col(12)[31].value,
             s2.col(12)[41].value, s2.col(12)[51].value, s2.col(12)[71].value]
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue", label='recall=1.0')
        plt.axis([0, 8000, 50, 110])

        y = [s2.col(12)[2].value, s2.col(12)[12].value, s2.col(12)[22].value, s2.col(12)[32].value,
             s2.col(12)[42].value, s2.col(12)[52].value, s2.col(12)[72].value]
        plt.plot(x, y, color="blue", marker="^", markerfacecolor="blue", label='recall=0.9')
        plt.axis([0, 8000, 50, 110])

        y = [s2.col(12)[3].value, s2.col(12)[13].value, s2.col(12)[23].value, s2.col(12)[33].value,
             s2.col(12)[43].value, s2.col(12)[53].value, s2.col(12)[73].value]
        plt.plot(x, y, color="blue", marker=">", markerfacecolor="blue", label='recall=0.8')
        plt.axis([0, 8000, 50, 110])

        y = [s2.col(12)[4].value, s2.col(12)[14].value, s2.col(12)[24].value, s2.col(12)[34].value,
             s2.col(12)[44].value, s2.col(12)[54].value, s2.col(12)[74].value]
        plt.plot(x, y, color="blue", marker="<", markerfacecolor="blue", label='recall=0.7')
        plt.axis([0, 8000, 50, 110])

        y = [s2.col(12)[5].value, s2.col(12)[15].value, s2.col(12)[25].value, s2.col(12)[35].value,
             s2.col(12)[45].value, s2.col(12)[55].value, s2.col(12)[75].value]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='recall=0.6')
        plt.axis([0, 8000, 50, 110])

        plt.legend()
        plt.show()

    if scheme == 5:
        x = [600, 1200, 1800, 2400, 3000, 3600]

        plt.figure(1)
        plt.xlabel("omega")
        plt.ylabel("speed up (%)")
        y = [s2.col(12)[6].value, s2.col(12)[16].value, s2.col(12)[26].value, s2.col(12)[36].value,
             s2.col(12)[46].value, s2.col(12)[56].value]
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue", label='precision=1.0')
        plt.axis([0, 4000, 50, 110])

        y = [s2.col(12)[7].value, s2.col(12)[17].value, s2.col(12)[27].value, s2.col(12)[37].value,
             s2.col(12)[47].value, s2.col(12)[57].value]
        plt.plot(x, y, color="blue", marker="^", markerfacecolor="blue", label='precision=0.9')
        plt.axis([0, 4000, 50, 110])

        y = [s2.col(12)[8].value, s2.col(12)[18].value, s2.col(12)[28].value, s2.col(12)[38].value,
             s2.col(12)[48].value, s2.col(12)[58].value]
        plt.plot(x, y, color="blue", marker=">", markerfacecolor="blue", label='precision=0.8')
        plt.axis([0, 4000, 50, 110])

        y = [s2.col(12)[9].value, s2.col(12)[19].value, s2.col(12)[29].value, s2.col(12)[39].value,
             s2.col(12)[49].value, s2.col(12)[59].value]
        plt.plot(x, y, color="blue", marker="<", markerfacecolor="blue", label='precision=0.7')
        plt.axis([0, 4000, 50, 110])

        y = [s2.col(12)[10].value, s2.col(12)[20].value, s2.col(12)[30].value, s2.col(12)[40].value,
             s2.col(12)[50].value, s2.col(12)[60].value]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='precision=0.6')
        plt.axis([0, 4000, 50, 110])

        plt.legend()
        plt.show()

    if scheme == 11:
        plt.figure(1)
        plt.title("size ~ effect")
        plt.xlabel("max size (KB)")
        plt.ylabel("speed up (%)")
        plt.axis([0, 22000, 0, 110])

        x = s1.col_values(6, start_rowx=1, end_rowx=30)
        y = s1.col_values(11, start_rowx=1, end_rowx=30)
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize')

        y = s3.col_values(11, start_rowx=1, end_rowx=30)
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs')

        plt.legend()
        plt.show()

    if scheme == 12:
        plt.title("omega++  (max size=10MB")
        plt.xlabel("omega")
        plt.ylabel("speed up (%)")
        plt.axis([580, 1220, 0, 110])

        x = s1.col_values(1, start_rowx=30, end_rowx=41)
        y = s1.col_values(11, start_rowx=30, end_rowx=41)
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize')

        y = s3.col_values(11, start_rowx=30, end_rowx=41)
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs')

        plt.legend()
        plt.show()

    if scheme == 13:
        plt.title("recall<-->omega effect (max size=10MB")
        plt.xlabel("omega")
        plt.ylabel("speed up (%)")
        plt.axis([580, 1220, 0, 110])

        x = s2.col_values(1)[41:92:5]
        y = s2.col_values(12)[41:92:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-1.0')
        y = s4.col_values(12)[41:92:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-1.0')
        plt.show()
        y = s2.col_values(12)[42:93:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.9')
        y = s4.col_values(12)[42:93:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.9')

        y = s2.col_values(12)[43:94:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.8')
        y = s4.col_values(12)[43:94:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.8')

        y = s2.col_values(12)[44:95:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.7')
        y = s4.col_values(12)[44:95:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.7')

        y = s2.col_values(12)[45:96:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.6')
        y = s4.col_values(12)[45:96:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.6')

        plt.legend()


    if scheme == 14:
        plt.title("precision<-->omega effect (max size=10MB")
        plt.xlabel("omega")
        plt.ylabel("speed up (%)")
        plt.axis([580, 1220, 0, 110])

        x = s2.col_values(1)[96:147:5]
        y = s2.col_values(12)[96:147:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-1.0')
        y = s4.col_values(12)[96:147:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-1.0')

        y = s2.col_values(12)[97:148:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.9')
        y = s4.col_values(12)[97:148:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.9')

        y = s2.col_values(12)[98:149:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.8')
        y = s4.col_values(12)[98:149:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.8')

        y = s2.col_values(12)[99:150:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.7')
        y = s4.col_values(12)[99:150:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.7')

        y = s2.col_values(12)[100:151:5]
        plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize-0.6')
        y = s4.col_values(12)[100:151:5]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs-0.6')

        plt.legend()
        plt.show()

    if scheme == 15:
        plt.figure(1)
        for i in xrange(9):
            plt.subplot(331+i)
            plt.title(str(600+i*60)+"s", fontsize=9)
            plt.axis([0.5, 1.1, 0, 110])
            x = s2.col_values(9)[(41+i*5):(46+i*5)]
            y = s2.col_values(12)[(41+i*5):(46+i*5)]
            plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize')
            y = s4.col_values(12)[(41+i*5):(46+i*5)]
            plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs')
            plt.legend(loc="upper left", fontsize=9)

        plt.figure(2)
        for i in xrange(9):
            plt.subplot(331+i)
            plt.title(str(600+i*60)+"s", fontsize=9)
            plt.axis([0.5, 1.1, 0, 110])
            x = s2.col_values(10)[(96+i*5):(101+i*5)]
            y = s2.col_values(12)[(96+i*5):(101+i*5)]
            plt.plot(x, y, color="green", marker="o", markerfacecolor="green", label='optimize')
            y = s4.col_values(12)[(96+i*5):(101+i*5)]
            plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='fcfs')
            plt.legend(loc="upper left", fontsize=9)
        plt.show()


draw("D:\Experiment\prefetching-simulation\project\plan_b\\result.xls", 15)


