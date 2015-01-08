#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xlrd
import random
import operator
import copy
import math
import pulp


ARGS1 = "D:\Experiment\prefetching-simulation\data\\args.xlsx"


def pause():
    if raw_input("press any key to continue:"):
        pass


def load_args():
    """load arguments from .xls"""

    xls = xlrd.open_workbook(ARGS1)
    table = xls.sheet_by_index(0)
    args = {}

    for i in xrange(table.nrows):
        args[table.cell(i, 0).value] = table.cell(i, 1).value

    for k, v in args.iteritems():
        if isinstance(v, float) and k != "recall" and k != "precision":
            args[k] = int(v)

    args["t"] = args["tn"] * args["tl"]
    args["n"] = args["t"] / args["f"]

    return args


def poisson(args):
    """generate a integer sequence under poisson distribution"""
    lamda = 1.0 / args["f"]
    ti = 0.0
    seq = []
    while True:
        ti += random.expovariate(lamda)
        if int(ti) >= args["t"]:
            break
        else:
            seq.append(int(ti))

    return seq


def uniform(args, n, use=""):
    """generate a integer sequence under uniform random distribution"""
    seq = []
    if use == "time":
        for i in xrange(n):
            seq.append(random.randint(0, args["t"]))
        seq.sort()
    elif use == "size":
        for i in xrange(n):
            seq.append(random.randint(args["mins"], args["maxs"]))
    else:
        print "need a 'use' argument for generate uniform data."
        exit()

    return seq


def gen_base(args):
    """generate arrival queue"""

    queue = []
    time_seq = []
    size_seq = []
    if args["dis"] == "poisson":
        time_seq = poisson(args)
        args["n"] = len(time_seq)
        size_seq = uniform(args, args["n"], "size")
    elif args["dis"] == "uniform":
        time_seq = uniform(args, args["n"], "time")
        size_seq = uniform(args, args["n"], "size")
    else:
        print "need an argument for data distribution."
        exit()

    for i in xrange(args["n"]):
        queue.append(Request(args))
        queue[i].at = time_seq[i] / args["tl"]
        queue[i].size = size_seq[i]
        queue[i].left = queue[i].size

    return queue


def load_base(args, pos):
    """load arrival queue from .xls"""

    print "loading data..."

    rfile = args["data1"]
    sheet_index = pos[0]
    time_col = pos[1]
    size_col = pos[2]
    start_row = pos[3]
    end_row = pos[4]

    xls_file = xlrd.open_workbook(rfile)
    table = xls_file.sheet_by_index(sheet_index)
    time = table.col_value(time_col)
    size = table.col_value(size_col)
    args["n"] = end_row - start_row + 1
    start_time = int(time[start_row] * 24)
    end_time = int(time[end_row] * 24) + 1
    args["t"] = (end_time - start_time) * 3600
    args["tn"] = int(math.ceil(args["t"] / float(args["tl"])))
    args["f"] = args["t"] / args["n"]
    args["maxs"] = int(max(size[start_row:end_row+1]))
    args["mins"] = int(min(size[start_row:end_row+1]))

    queue = []
    for i in range(start_row, end_row + 1):
        queue.append(Request(args))
        queue[i].at = (int(time[i] * 24 * 60 * 60) - start_time * 60 * 60) / args["tl"]
        queue[i].size = int(size[i])
        queue[i].left = queue[i].size

    return queue


def gen_extra(queue, args, accuracy=(1.0, 1.0)):
    """generate deviation data
       input: arrival queue
       output: predicted(hit+false) queue, submitted(hit+false+miss) queue, arrival(hit+miss) queue
    """

    recall = accuracy[0]
    precision = accuracy[1]
    hit = int(recall*args["n"])
    miss = args["n"]-hit
    false = int(((1.0-precision)/precision)*hit)

    # false queue
    f_queue = []
    time_seq = uniform(args, false, "time")
    size_seq = uniform(args, false, "size")
    for i in xrange(false):
        f_queue.append(Request(args))
        f_queue[i].at = time_seq[i] / args["tl"]
        f_queue[i].size = size_seq[i]
        f_queue[i].left = f_queue[i].size
        f_queue[i].flag = "false"

    # arrival queue
    for i in random.sample(xrange(len(queue)), miss):
        queue[i].flag = "miss"

    a_queue = copy.deepcopy(queue)

    # miss queue
    m_queue = []
    for r in queue[::-1]:
        if r.flag == "miss":
            m_queue.append(queue.pop(queue.index(r)))

    # predicted queue
    queue.extend(f_queue)
    queue = sorted(queue, key=operator.attrgetter("at"))

    for i,r in enumerate(queue):
        r.id = i

    p_queue = copy.deepcopy(queue)

    # submitted queue
    queue.extend(m_queue)
    queue = sorted(queue, key=operator.attrgetter("at"))

    return p_queue, queue, a_queue


def inh_data(queue1, queue2, args):
    """queue1 inherit from queue2"""

    for r in queue1:
        if r.id != args["ot"]:
            r.bdt = queue2[r.id].ft
            for t in xrange(args["t"]):
                r.b[t] = queue2[r.id].b[t]


def simulate(args, queue, scheduled=False, perfect=True):
    """simulate request events"""
    tn = args["tn"]
    tl = args["tl"]
    B = args["b"]
    ot = args["ot"]
    ureq_recorder = []

    if not scheduled:
        nreq_recorder = []
        for t in xrange(tn):
            for r in queue:
                if r.at <= t and r.left > 0 and (r not in nreq_recorder):
                    nreq_recorder.append(r)

            for r in nreq_recorder:
                r.left -= (B / len(nreq_recorder)) * tl
                r.debug_b[t] = B / len(nreq_recorder)

            for r in nreq_recorder[::-1]:
                if r.left <= 0:
                    r.ft = t
                    nreq_recorder.pop(nreq_recorder.index(r))

        for r in queue:
            if r.left <= 0:
                r.wt = r.ft - r.at + 1
                r.gsize = r.size
                r.left = 0
            else:
                r.ft = tn - 1
                r.wt = r.ft - r.at + 1
                r.gsize = r.size - r.left
                ureq_recorder.append(r)
    else:
        preq_recorder = []
        nreq_recorder = []
        mreq_recorder = []

        for t in xrange(tn):
            for r in queue:
                if r.left > 0 and r not in mreq_recorder and r not in preq_recorder and r not in nreq_recorder:
                    if r.flag != "miss":
                        if r.at > t:
                            preq_recorder.append(r)
                        else:
                            nreq_recorder.append(r)
                    elif r.at <= t:
                        mreq_recorder.append(r)

            for r in preq_recorder[::-1]:
                if r.at <= t:
                    nreq_recorder.append(preq_recorder.pop(preq_recorder.index(r)))

            if not perfect:
                for r in nreq_recorder[::-1]:
                    if r.bdt < t:
                        mreq_recorder.append(nreq_recorder.pop(nreq_recorder.index(r)))

            if perfect and len(mreq_recorder) != 0:
                print "schedule wrong."
                exit()

            for r in preq_recorder:
                if len(mreq_recorder) == 0:
                    r.left -= r.b[t] * tl
                    r.psize += r.b[t] * tl
                    r.debug_b[t] = r.b[t]

            for r in nreq_recorder:
                if len(mreq_recorder) == 0:
                    r.left -= r.b[t] * tl
                    r.debug_b[t] = r.b[t]
                else:
                    r.left -= (B / (len(mreq_recorder) + len(nreq_recorder))) * tl
                    r.debug_b[t] = B / (len(mreq_recorder) + len(nreq_recorder))

            for r in mreq_recorder:
                r.left -= (B / (len(mreq_recorder) + len(nreq_recorder))) * tl
                r.debug_b[t] = B / (len(mreq_recorder) + len(nreq_recorder))

            for r in queue:
                if r.left <= 0 and r.ft == ot:
                    if r.at > t:
                        r.ft = r.at - 1
                    else:
                        r.ft = t

                    if r in preq_recorder:
                        preq_recorder.pop(preq_recorder.index(r))
                    elif r in nreq_recorder:
                        nreq_recorder.pop(nreq_recorder.index(r))
                    elif r in mreq_recorder:
                        mreq_recorder.pop(mreq_recorder.index(r))

        for r in queue:
            if r.left <= 0:
                r.wt = r.ft - r.at + 1
                r.gsize = r.size
                r.left = 0
            else:
                r.ft = tn - 1
                r.wt = r.ft - r.at + 1
                r.gsize = r.size - r.left
                ureq_recorder.append(r)

    return ureq_recorder


def schedule(args, queue1, queue2):
    """solve lp problem"""

    tl = args["tl"]
    idx = range(args["n"])
    tdx = range(args["tn"])
    ti = range(args["n"])
    si = range(args["n"])
    Ti = range(args["n"])
    Si = range(args["n"])

    for i in xrange(args["n"]):
        ti[i] = queue1[i].at
        si[i] = queue1[i].gsize
        Ti[i] = queue1[i].ft
        Si[i] = queue1[i].size
        idx[i] = str(i)

    for t in xrange(args["tn"]):
        tdx[t] = str(t)

    """----------------------------------------
        PuLP variable definition
        varb--bi(t)
        prob--objective and constraints

        objective:
            max:[0~n-1][0~ti-1])sigma bi(t)

        constraints:
            1.any t,[0~n-1] sigma bi(t)   <= B
            2.any i,[0-Ti]  sigma bi(t)*tl>= si
            3.any i,[0~T-1] sigma bi(t)*tl<= Si
    ----------------------------------------"""
    print "\ndefine lp variables"
    varb = pulp.LpVariable.dicts('b', (idx,tdx), 0, args["b"], cat='Integer')

    print "define lp problem"
    prob = pulp.LpProblem('Prefetching Schedule', pulp.LpMaximize)

    print "define lp objective"
    prob += pulp.lpSum([tl*varb[i][t] for i in idx for t in tdx if int(t)<ti[int(i)]])

    print "define constraints on B"
    for t in tdx:
        prob += pulp.lpSum([varb[i][t] for i in idx]) <= args["b"]

    print "define constraints on si"
    for i in idx:
        #print i,int(i),si[int(i)],Ti[int(i)]
        #print [tl*varb[i][t] for t in tdx if int(t)<=Ti[int(i)]]
        #pause()
        prob += pulp.lpSum([tl*varb[i][t] for t in tdx if int(t)<=Ti[int(i)]]) >= si[int(i)]


    print "define constraints on Si"
    for i in idx:
        prob += pulp.lpSum([tl*varb[i][t] for t in tdx]) == Si[int(i)]

    prob_status = pulp.LpStatusNotSolved
    if args["solver"] == "default" or args["solver"] == "":
        print "solve lp problem using default solver."
        prob_status = prob.solve()
    elif args["solver"] == "GLPK":
        print "solve lp problem using GLPK solver."
        prob_status = prob.solve(pulp.GLPK())
    else:
        print "wrong solver argument."
        exit()

    print "Problem solved. Status: " + pulp.LpStatus[prob_status]

    for i in xrange(args["n"]):
        for t in xrange(args["tn"]):
            queue2[i].b[t] = int(math.ceil(pulp.value(varb[str(i)][str(t)])))

    #print varb
    return varb


def stats(queue1, u1, queue2, u2, accuracy=(1.0, 1.0)):
    """statistics about schedule"""

    # 0  : total_size
    # 1  : total_gsize1
    # 2  : total_gsize2
    # 3  : total_gsize_increased
    # 4  : total_wtime1
    # 5  : total_wtime2
    # 6  : total_wtime_decreased
    # 7  : total_psize
    # 8  : miss_wtime_decreased
    # 9  : false_traffic
    # 10 : hit_wtime_decreased
    # 11 : req_decelerated
    # 12 : req_accelerated
    # 13 : unfinished_req_before
    # 14 : unfinished_req_after

    res = [0 for i in xrange(15)]

    for i,r in enumerate(queue2):
        res[0] += r.size
        res[1] += queue1[i].gsize
        res[2] += r.gsize
        res[4] += queue1[i].wt
        res[5] += r.wt
        res[7] += r.psize

        if r.flag == "miss":
            res[8] += queue1[i].wt-r.wt
        elif r.flag == "false":
            res[9] += r.gsize
        else:
            res[10] += queue1[i].wt-r.wt

        if queue1[i].wt-r.wt < 0:
            res[11] += 1
        elif queue1[i].wt-r.wt > 0:
            res[12] += 1

    res[1] = res[1]*100.0/res[0]
    res[2] = res[2]*100.0/res[0]
    res[3] = (res[2]-res[1])*100.0/res[0]
    res[6] = (res[4]-res[5])*100.0/res[4]
    res[7] = res[7]*100.0/res[0]
    res[8] = res[8]*100.0/res[4]
    res[9] = res[9]*100.0/res[0]
    res[10] = res[10]*100.0/res[4]
    res[11] = res[11]*100.0/len(queue2)
    res[12] = res[12]*100.0/len(queue2)
    res[13] = len(u1)*100.0/len(queue2)
    res[14] = len(u2)*100.0/len(queue2)

    if accuracy == (1.0, 1.0):
        res[8] = 0.0
        res[9] = 0.0
        res[10] = 0.0

    return res


def output(args, res, tag="wrong"):
    """output the simulate result to console and file"""

    print "\nThis is the "+tag+" result."
    if tag == "perfect" :
        print "-------------------------------------------------------"
        print "| parameters:"
        print "| T: %d*%d, F: %d, N: %d, dis: %s" % (args["tn"],args["tl"],args["f"],args["n"],args["dis"])
        print "| max size: %.1f KB, min size: %.1f KB" % (args["maxs"]/1024.0, args["mins"]/1024.0)
        print "| recall : %.1f, precision: %.1f" % (args["recall"], args["precision"])
    print "-------------------------------------------------------"
    print "| waiting time decreased for all  : %.1f%%" % res[6]
    print "| waiting time decreased for hit  : %.1f%%" % res[10]
    print "| waiting time decreased for miss : %.1f%%" % res[8]
    print "| accelerated request             : %.1f%%" % res[12]
    print "| decelerated request             : %.1f%%" % res[11]
    print "| data prefetched                 : %.1f%%" % res[7]
    print "| finished data increase          : %.1f%%" % res[3]
    print "| false traffic ratio             : %.1f%%" % res[9]
    print "| unfinished req before schedule  : %.1f%%" % res[13]
    print "| unfinished req after schedule   : %.1f%%" % res[14]
    print "-------------------------------------------------------"


def debug(args, q1, q2):
    """print dedug information on console"""
    print"\n"

    print "------------------"
    print "| before schedule."
    print "-------------------------------------------------------------"
    for i,r in enumerate(q1):
        print "r%3d,ti:%3d,Ti:%3d,Si:%7.1fKB,wt:%3d,*:%5s,si:%5.1f" % \
              (i, r.at, r.ft, r.size/1024.0, r.wt, r.flag, r.gsize*100.0/r.size)
    print "-------------------------------------------------------------"
    print "------------------"
    print "| after schedule."
    print "----------------------------------------------------------------------------------------------"
    for i,r in enumerate(q2):
        print "r%3d,ti:%3d,Ti:%3d,Si:%7.1fKB,wt:%3d,*:%5s,si:%5.1f,wt(-):%5.1f%%,ps:%5.1f%%,si+:%4.1f%%,bdt:%3d"\
              % (i, r.at, r.ft, r.size/1024.0, r.wt, r.flag, r.gsize*100.0/r.size, (q1[i].wt-r.wt)*100.0/q1[i].wt,
               r.psize*100.0/r.size, (r.gsize-q1[i].gsize)*100.0/r.size, r.bdt)
    print "----------------------------------------------------------------------------------------------"
    pause()

    #print "------------------"
    #print "| abnormal request"
    #print "------------------"
    #for i,r in enumerate(q2):
    #    if q1[i].wt-r.wt < 0:
    #        print "r%3d" % i
    #        for t in xrange(args["t"]):
    #            print "t:%3d, b:%5.1f, cb:%5.1f, db:%5.1f" % (t, r.b[t]/1024.0, q1[i].debug_b[t]/1024.0, q2[i].debug_b[t]/1024.0)
    #        pause()


class Request(object):
    """class for all requests"""

    def __init__(self, args):
        """init function"""

        ot = args["ot"]
        tn = args["tn"]

        self.at = ot        # arrival time
        self.ft = ot        # finish time
        self.wt = ot        # waiting time
        self.size = 0       # req data size
        self.gsize = 0      # data size of req got in [0,T]
        self.psize = 0      # prefetched size
        self.left = 0       # left size
        self.flag = "hit"   # req category flag : miss,false,hit
        self.bdt = ot       # bdp,boundary timepoint
        self.id = ot        # id in predicted queue
        self.b = [0 for i in xrange(tn)]         # bandwidth for ri at timeslot t in b
        self.debug_b = [0 for i in xrange(tn)]