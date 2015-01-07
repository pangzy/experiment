#!/usr/bin/env python
# -*- coding: utf-8 -*-		

import xlrd

"""global variables definition"""
#TL = TIMESLOT_LENGTH    = 1         # 0, second
#TN = TIMESLOT_NUMBER    = 600       # 1,
#T  = TIME               = TN * TL   # 2, TN*TL = total time in time zone
#F  = REQUEST_FREQUENCY  = 10        # 3, request frequency , seconds/req, F=T/N
#N  = REQUEST_NUMBER     = (T / F)   # 4, request number in a
#B  = BANDWIDTH          = 512       # 5, KB/s
#OT = TIME_OUT_OF_RANGE  = -1        # 6, time out of [0,T]
#MAXS = MAX_SINGLE_SIZE  = 400       # 7, KB
#MINS = MIN_SINGLE_SIZE  = 1         # 8, KB
#
#DATA1 = "D:\Experiment\prefetching-simulation\data2.xls"        # 9
#RESULT1 = "D:\Experiment\prefetching-simulation\\result.xls"    # 10

ARGS1 = "D:\Experiment\prefetching-simulation\data\\args.xlsx"  # 11
args = {}

def load_args():
    """load arguments from file"""
    xls = xlrd.open_workbook(ARGS1)
    table = xls.sheet_by_index(0)

    for i in xrange(table.nrows):
        args[table.cell(i, 0).value] = table.cell(i, 1).value

    for k,v in args.iteritems():
        if isinstance(v,float) and k != "recall" and k != "precise":
            args[k] = int(v)
        else:
            pass

    args["t"] = args["tn"]*args["tl"]
    args["n"] = args["t"] / args["f"]


def get_glv():
    return args


def set_tl(tl):
    args["tl"] = tl


def set_tn(tn):
    args["tn"] = tn


def set_t(t):
    args["t"] = t


def set_f(f):
    args["f"] = f


def set_n(n):
    args["n"] = n


def set_maxs(maxs):
    args["maxs"] = maxs


def set_mins(mins):
    args["mins"] = mins