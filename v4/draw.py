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
        plt.title("omega (200KB)")
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
        plt.title("600s (200KB)", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+11].value)
        plt.subplot(232)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("1200s (200KB)", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+21].value)
        plt.subplot(233)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("1800s (200KB)", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+31].value)
        plt.subplot(234)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("2400s (200KB)", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+41].value)
        plt.subplot(235)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("3000s (200KB)", fontsize=10)
        plt.xlabel("recall", fontsize=10)
        plt.ylabel("speed up (%)")
        plt.axis([0.5, 1.1, 50, 110])

        y = []
        for j in xrange(5):
            y.append(s2.col(12)[j+51].value)
        plt.subplot(236)
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue")
        plt.title("3600s (200KB)", fontsize=10)
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
        x = [600, 1200, 1800, 2400, 3000, 3600, 7200, 10800]

        plt.figure(1)
        plt.xlabel("omega (200KB)")
        plt.ylabel("speed up (%)")
        y = [s2.col(12)[1].value, s2.col(12)[11].value, s2.col(12)[21].value, s2.col(12)[31].value,
             s2.col(12)[41].value, s2.col(12)[51].value, s2.col(12)[71].value, s2.col(12)[81].value]
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue", label='recall=1.0')
        plt.axis([0, 11000, 50, 110])

        y = [s2.col(12)[2].value, s2.col(12)[12].value, s2.col(12)[22].value, s2.col(12)[32].value,
             s2.col(12)[42].value, s2.col(12)[52].value, s2.col(12)[72].value, s2.col(12)[82].value]
        plt.plot(x, y, color="blue", marker="^", markerfacecolor="blue", label='recall=0.9')
        plt.axis([0, 11000, 50, 110])

        y = [s2.col(12)[3].value, s2.col(12)[13].value, s2.col(12)[23].value, s2.col(12)[33].value,
             s2.col(12)[43].value, s2.col(12)[53].value, s2.col(12)[73].value, s2.col(12)[83].value]
        plt.plot(x, y, color="blue", marker=">", markerfacecolor="blue", label='recall=0.8')
        plt.axis([0, 11000, 50, 110])

        y = [s2.col(12)[4].value, s2.col(12)[14].value, s2.col(12)[24].value, s2.col(12)[34].value,
             s2.col(12)[44].value, s2.col(12)[54].value, s2.col(12)[74].value, s2.col(12)[84].value]
        plt.plot(x, y, color="blue", marker="<", markerfacecolor="blue", label='recall=0.7')
        plt.axis([0, 11000, 50, 110])

        y = [s2.col(12)[5].value, s2.col(12)[15].value, s2.col(12)[25].value, s2.col(12)[35].value,
             s2.col(12)[45].value, s2.col(12)[55].value, s2.col(12)[75].value, s2.col(12)[85].value]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='recall=0.6')
        plt.axis([0, 11000, 50, 110])

        plt.legend()
        plt.show()

    if scheme == 5:
        x = [600, 1200, 1800, 2400, 3000, 3600, 7200]

        plt.figure(1)
        plt.xlabel("omega (200KB)")
        plt.ylabel("speed up (%)")
        y = [s2.col(12)[6].value, s2.col(12)[16].value, s2.col(12)[26].value, s2.col(12)[36].value,
             s2.col(12)[46].value, s2.col(12)[56].value, s2.col(12)[76].value]
        plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue", label='precision=1.0')
        plt.axis([0, 7400, 50, 110])

        y = [s2.col(12)[7].value, s2.col(12)[17].value, s2.col(12)[27].value, s2.col(12)[37].value,
             s2.col(12)[47].value, s2.col(12)[57].value, s2.col(12)[77].value]
        plt.plot(x, y, color="blue", marker="^", markerfacecolor="blue", label='precision=0.9')
        plt.axis([0, 7400, 50, 110])

        y = [s2.col(12)[8].value, s2.col(12)[18].value, s2.col(12)[28].value, s2.col(12)[38].value,
             s2.col(12)[48].value, s2.col(12)[58].value, s2.col(12)[78].value]
        plt.plot(x, y, color="blue", marker=">", markerfacecolor="blue", label='precision=0.8')
        plt.axis([0, 7400, 50, 110])

        y = [s2.col(12)[9].value, s2.col(12)[19].value, s2.col(12)[29].value, s2.col(12)[39].value,
             s2.col(12)[49].value, s2.col(12)[59].value, s2.col(12)[79].value]
        plt.plot(x, y, color="blue", marker="<", markerfacecolor="blue", label='precision=0.7')
        plt.axis([0, 7400, 50, 110])

        y = [s2.col(12)[10].value, s2.col(12)[20].value, s2.col(12)[30].value, s2.col(12)[40].value,
             s2.col(12)[50].value, s2.col(12)[60].value, s2.col(12)[80].value]
        plt.plot(x, y, color="blue", marker="s", markerfacecolor="blue", label='precision=0.6')
        plt.axis([0, 7400, 50, 110])

        plt.legend()
        plt.show()

    if scheme == 6:
        plt.figure(1)
        for i in xrange(8):
            plt.subplot(241+i)
            plt.title(str(int(s2.col_values(1)[1+i*10]))+"s"+"  (200KB)", fontsize=9)
            plt.axis([0.5, 1.1, 0, 110])
            x = s2.col_values(9)[(1+i*10):(6+i*10)]
            y = s2.col_values(12)[(1+i*10):(6+i*10)]
            plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue", label='optimize')
            plt.legend(loc="upper left", fontsize=9)

        plt.figure(2)
        for i in xrange(7):
            plt.subplot(241+i)
            plt.title(str(int(s2.col_values(1)[1+i*10]))+"s"+"  (200KB)", fontsize=9)
            plt.axis([0.5, 1.1, 0, 110])
            x = s2.col_values(10)[(6+i*10):(11+i*10)]
            y = s2.col_values(12)[(6+i*10):(11+i*10)]
            plt.plot(x, y, color="blue", marker="o", markerfacecolor="blue", label='optimize')
            plt.legend(loc="upper left", fontsize=9)
        plt.show()


draw("D:\Experiment\prefetching-simulation\data\gen\\result.xls", 6)


