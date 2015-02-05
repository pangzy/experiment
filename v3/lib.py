#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xlrd import *
# from xlwt import *
from xlutils.copy import copy
from pulp import *
from random import *
from operator import attrgetter
from math import ceil
from ConfigParser import ConfigParser
# from pyomo.environ import *
# from pyomo.opt import SolverFactory
import platform

def pause():
    if raw_input("press any key to continue:"):
        pass


def load_glbv():
    """load global variables from .xls"""
    glbv = {}
    glbv["path"] = ""
    glbv["config_file"] = ""

    if platform.system() == "Windows":
        glbv["path"] = "D:\Experiment\prefetching-simulation"
        glbv["config_file"] = glbv["path"]+"\project\glbv.conf"
    elif platform.system() == "Linux":
        glbv["path"] = "/home/pzy/test"
        glbv["config_file"] = glbv["path"]+"/glbv.conf"

    cf = ConfigParser()
    cf.read(glbv["config_file"])

    glbv["tl"] = cf.getint("glbv", "tl")
    glbv["tn"] = cf.getint("glbv", "tn")
    glbv["t"] = cf.getint("glbv", "t")
    glbv["f"] = cf.getint("glbv", "f")
    glbv["n"] = cf.getint("glbv", "n")
    glbv["b"] = cf.getint("glbv", "b")
    glbv["ot"] = cf.getint("glbv", "ot")
    glbv["maxs"] = cf.getint("glbv", "maxs")
    glbv["mins"] = cf.getint("glbv", "mins")
    glbv["recall"] = cf.getfloat("glbv", "recall")
    glbv["precision"] = cf.getfloat("glbv", "precision")
    glbv["source"] = cf.get("glbv", "source")
    glbv["solver"] = cf.get("glbv", "solver")
    glbv["dis"] = cf.get("glbv", "dis")
    glbv["wrt"] = cf.get("glbv", "wrt")
    glbv["draw"] = cf.get("glbv", "draw")
    glbv["data1"] = cf.get("glbv", "data1")
    glbv["result1"] = cf.get("glbv", "result1")
    glbv["sheet_index"] = cf.getint("glbv", "sheet_index")
    glbv["time_col"] = cf.getint("glbv", "time_col")
    glbv["size_col"] = cf.getint("glbv", "size_col")
    glbv["start_row"] = cf.getint("glbv", "start_row")
    glbv["end_row"] = cf.getint("glbv", "end_row")

    glbv["t"] = glbv["tn"]*glbv["tl"]
    glbv["n"] = glbv["t"]/glbv["f"]

    if platform.system() == "Windows":
        glbv["data_file"] = glbv["path"]+"\\project\\"+glbv["data1"]
        glbv["result_file"] = glbv["path"]+"\\project\\"+glbv["result1"]
    elif platform.system() == "Linux":
        glbv["data_file"] = glbv["path"]+"/"+glbv["data1"]
        glbv["result_file"] = glbv["path"]+"/"+glbv["result1"]

    return glbv


def rdm_poi(f, bound):
    """generate a integer sequence under poisson distribution"""
    lamda = 1.0/f
    ti = 0.0
    seq = []
    while True:
        ti += expovariate(lamda)
        if int(ti) >= bound:
            break
        else:
            seq.append(int(ti))

    return seq


def rdm_uni(lower, upper, n, sort=False):
    """generate a integer sequence under uniform random distribution"""
    seq = [randint(lower, upper) for i in xrange(n)]
    if sort:
        seq.sort()

    return seq


def gen_base(glbv):
    """generate arrival queue"""

    queue = []
    time_seq = []
    size_seq = []
    if glbv["dis"] == "poisson":
        time_seq = rdm_poi(glbv["f"], glbv["t"])
        glbv["n"] = len(time_seq)
        size_seq = rdm_uni(glbv["mins"], glbv["maxs"], glbv["n"])
    elif glbv["dis"] == "uniform":
        time_seq = rdm_uni(0, glbv["t"]-1, glbv["n"], sort=True)
        size_seq = rdm_uni(glbv["mins"], glbv["maxs"], glbv["n"])
    else:
        print "need an argument for data distribution."
        exit()

    for i in xrange(len(time_seq)):
        queue.append(Request(glbv))
        queue[i].at = time_seq[i]/glbv["tl"]
        queue[i].size = size_seq[i]
        queue[i].left = queue[i].size

    return queue


def load_base(glbv):
    """load arrival queue from .xls"""

    print "loading data..."

    rfile = glbv["data_file"]
    sheet_index = glbv["sheet_index"]
    time_col = glbv["time_col"]
    size_col = glbv["size_col"]
    start_row = glbv["start_row"]
    end_row = glbv["end_row"]

    xls_file = open_workbook(rfile)
    table = xls_file.sheet_by_index(sheet_index)
    time = table.col_values(time_col)
    size = table.col_values(size_col)
    glbv["n"] = end_row-start_row+1
    start_time = int(time[start_row]*24*60)
    end_time = int(time[end_row]*24*60)+1
    glbv["t"] = (end_time-start_time)*60
    glbv["tn"] = int(ceil(glbv["t"]/float(glbv["tl"])))
    glbv["f"] = glbv["t"]/float(glbv["n"])
    glbv["maxs"] = int(max(size[start_row:end_row+1]))
    glbv["mins"] = int(min(size[start_row:end_row+1]))

    queue = []
    for i in range(start_row, end_row + 1):
        r = Request(glbv)
        r.at = (int(time[i]*24*60*60)-start_time*60)/glbv["tl"]
        r.size = int(size[i])
        r.left = r.size
        queue.append(r)

    return queue


def clone_queue(glbv, q):
    cq = []
    for i in xrange(len(q)):
        cq.append(Request(glbv))
        cq[i].at = q[i].at
        cq[i].size = q[i].size
        cq[i].left = q[i].left
        cq[i].flag = q[i].flag
        cq[i].id = q[i].id

    return cq


def gen_deviation(queue, glbv):
    """generate deviation data
       input: arrival queue
       output: predicted(hit+false) queue, submitted(hit+false+miss) queue, arrival(hit+miss) queue
    """

    recall = glbv["recall"]
    precision = glbv["precision"]
    hit = int(recall*glbv["n"])
    miss = glbv["n"]-hit
    false = int(((1.0-precision)/precision)*hit)

    # false queue
    f_queue = []
    time_seq = rdm_uni(0, glbv["t"]-1, false, sort=True)
    size_seq = rdm_uni(glbv["mins"], glbv["maxs"], false)
    for i in xrange(false):
        f_queue.append(Request(glbv))
        f_queue[i].at = time_seq[i]/glbv["tl"]
        f_queue[i].size = size_seq[i]
        f_queue[i].left = f_queue[i].size
        f_queue[i].flag = "false"

    # arrival queue
    for i in sample(xrange(len(queue)), miss):
        queue[i].flag = "miss"

    a_queue = clone_queue(glbv, queue)

    # miss queue
    m_queue = []
    for r in queue[::-1]:
        if r.flag == "miss":
            m_queue.append(queue.pop(queue.index(r)))

    # predicted queue
    queue.extend(f_queue)
    queue = sorted(queue, key=attrgetter("at"))

    for i,r in enumerate(queue):
        r.id = i

    p_queue = clone_queue(glbv, queue)

    # submitted queue
    queue.extend(m_queue)
    queue = sorted(queue, key=attrgetter("at"))

    return p_queue, queue, a_queue


def inh_data(queue1, queue2, glbv):
    """queue1 inherit from queue2"""

    for r in queue1:
        if r.id != glbv["ot"]:
            r.bdt = queue2[r.id].ft
            for t in xrange(glbv["t"]):
                r.b[t] = queue2[r.id].b[t]


def simulate(glbv, queue, q_type):
    """
    q_type :
        a : predict queue without schedule
        b : predict queue with schedule
        c : evaluation queue without schedule
        d : evaluation queue with schedule
        fcfs : first come first service with schedule
    """
    tn = glbv["tn"]
    tl = glbv["tl"]
    B = glbv["b"]
    ot = glbv["ot"]
    ureq_recorder = []
    nreq_recorder = []
    preq_recorder = []
    mreq_recorder = []

    if q_type == "a" or q_type == "c":
        for t in xrange(tn):
            for r in queue:
                if r.at <= t and r.left > 0 and (r not in nreq_recorder):
                    nreq_recorder.append(r)

            for r in nreq_recorder:
                r.left -= (B/len(nreq_recorder))*tl
                r.debug_b[t] = B/len(nreq_recorder)

            for r in nreq_recorder[::-1]:
                if r.left <= 0:
                    r.ft = t
                    nreq_recorder.pop(nreq_recorder.index(r))

        for r in queue:
            if r.left <= 0:
                r.wt = r.ft-r.at+1
                r.gsize = r.size
                r.left = 0
            else:
                r.ft = tn-1
                r.wt = r.ft-r.at+1
                r.gsize = r.size-r.left
                ureq_recorder.append(r)

    elif q_type == "b" or q_type == "d":
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

            if q_type == "d":
                for r in nreq_recorder[::-1]:
                    if r.bdt < t:
                        mreq_recorder.append(nreq_recorder.pop(nreq_recorder.index(r)))

            if q_type == "b" and len(mreq_recorder) != 0:
                print "schedule wrong."
                exit()

            for r in preq_recorder:
                if len(mreq_recorder) == 0:
                    r.left -= r.b[t]*tl
                    r.psize += r.b[t]*tl
                    r.debug_b[t] = r.b[t]

            for r in nreq_recorder:
                if len(mreq_recorder) == 0:
                    r.left -= r.b[t]*tl
                    r.debug_b[t] = r.b[t]
                else:
                    r.left -= (B/(len(mreq_recorder)+len(nreq_recorder)))*tl
                    r.debug_b[t] = B/(len(mreq_recorder)+len(nreq_recorder))

            for r in mreq_recorder:
                r.left -= (B/(len(mreq_recorder)+len(nreq_recorder)))*tl
                r.debug_b[t] = B/(len(mreq_recorder)+len(nreq_recorder))

            for r in queue:
                if r.left <= 0 and r.ft == ot:
                    if r.at > t:
                        r.ft = r.at-1
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
                r.wt = r.ft-r.at+1
                r.gsize = r.size
                r.left = 0
            else:
                r.ft = tn-1
                r.wt = r.ft-r.at+1
                r.gsize = r.size-r.left
                ureq_recorder.append(r)

    elif q_type == "fcfs":
        for t in xrange(tn):
            for r in queue:
                if r.left > 0 and r not in nreq_recorder:
                    if r.at <= t:
                        nreq_recorder.append(r)

            for r in preq_recorder[::-1]:
                if r.at <= t:
                    preq_recorder.pop(preq_recorder.index(r))

            if len(nreq_recorder) == 0:
                b_available = B

                for r in queue:
                    if sum([ceil(x.left/float(tl)) for x in preq_recorder]) >= b_available:
                        break

                    if r.at > t and r.flag != "miss" and r not in preq_recorder:
                        preq_recorder.append(r)

                for r in preq_recorder:
                    if ceil(r.left/float(tl)) <= b_available:
                        r.b[t] = ceil(r.left/float(tl))
                        b_available -= ceil(r.left/float(tl))
                    else:
                        r.b[t] = b_available
                        b_available = 0

                    r.left -= r.b[t]*tl
                    r.psize += r.b[t]*tl
            else:
                for r in nreq_recorder:
                    r.b[t] = B/len(nreq_recorder)
                    r.left -= r.b[t]*tl

            for r in queue:
                if r.left <= 0 and r.ft == ot:
                    if r.at > t:
                        r.ft = r.at-1
                    else:
                        r.ft = t

                    if r in preq_recorder:
                        preq_recorder.pop(preq_recorder.index(r))
                    elif r in nreq_recorder:
                        nreq_recorder.pop(nreq_recorder.index(r))

        for r in queue:
            if r.left <= 0:
                r.wt = r.ft-r.at+1
                r.gsize = r.size
                r.left = 0
            else:
                r.ft = tn-1
                r.wt = r.ft-r.at+1
                r.gsize = r.size-r.left
                ureq_recorder.append(r)

    return ureq_recorder


def schedule_pulp(glbv, queue1, queue2):
    """solve lp problem"""

    tl = glbv["tl"]

    ti = [r.at for r in queue1]
    si = [r.gsize for r in queue1]
    Ti = [r.ft for r in queue1]
    Si = [r.size for r in queue1]
    idx = [str(i) for i in xrange(glbv["n"])]
    tdx = [str(t) for t in xrange(glbv["tn"])]

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
    varb = LpVariable.dicts('b', (idx,tdx), 0, glbv["b"], cat='Integer')

    print "define lp problem"
    prob = LpProblem('Prefetching Schedule', LpMaximize)

    print "define lp objective"
    prob += lpSum([tl*varb[i][t] for i in idx for t in tdx if int(t) < ti[int(i)]])

    print "define constraints on B"
    for t in tdx:
        prob += lpSum([varb[i][t] for i in idx]) <= glbv["b"]

    print "define constraints on si"
    for i in idx:
        prob += lpSum([tl*varb[i][t] for t in tdx if int(t) <= Ti[int(i)]]) >= si[int(i)]


    print "define constraints on Si"
    for i in idx:
        prob += lpSum([tl*varb[i][t] for t in tdx]) <= Si[int(i)]

    prob_status = LpStatusNotSolved
    if glbv["solver"] == "default" or glbv["solver"] == "":
        print "solve lp problem using default solver."
        prob_status = prob.solve()
    elif glbv["solver"] == "GLPK":
        print "solve lp problem using GLPK solver."
        prob_status = prob.solve(GLPK())
    else:
        print "wrong solver argument."
        exit()

    print "Problem solved. Status: " + LpStatus[prob_status]

    for i in xrange(glbv["n"]):
        for t in xrange(glbv["tn"]):
            queue2[i].b[t] = int(ceil(value(varb[str(i)][str(t)])))

    return varb, prob.objective


def schedule_pyomo(glbv, queue1, queue2):
    ti = [r.at for r in queue1]
    si = [r.gsize for r in queue1]
    Ti = [r.ft for r in queue1]
    Si = [r.size for r in queue1]

    model = AbstractModel("schedule")
    model.n = Param(default=glbv["n"])
    model.T = Param(default=glbv["tn"])
    model.B = Param(default=glbv["b"])
    model.tl = Param(default=glbv["tl"])
    model.i = RangeSet(0, model.n-1)
    model.t = RangeSet(0, model.T-1)

    print "define var."
    model.b = Var(model.i, model.t, domain=NonNegativeIntegers, bounds=(0, model.B))

    print "define obj."
    def obj_rule(model):
        return sum(model.tl*model.b[i,t] for i in xrange(model.n) for t in xrange(ti[i]))
    model.obj = Objective(rule=obj_rule, sense=maximize)

    print "define constraints."
    def c1_rule(model, t):
        return sum(model.b[i,t] for i in xrange(model.n)) <= model.B
    model.c1 = Constraint(model.t, rule=c1_rule)

    def c2_rule(model, i):
        return sum(model.tl*model.b[i,t] for t in xrange(Ti[i]+1)) >= si[i]
    model.c2 = Constraint(model.i, rule=c2_rule)

    def c3_rule(model, i):
        return sum(model.tl*model.b[i,t] for t in xrange(model.T)) <= Si[i]
    model.c3 = Constraint(model.i, rule=c3_rule)

    print "solve problem."
    opt = SolverFactory("glpk")

    instance = model.create()
    result = opt.solve(instance)
    instance.load(result)

    print "\n%d solution found in pyomo." % len(result.solution)
    for i,r in enumerate(result.solution):
        print "  solution %d : %s" % (i+1, r.status)

    for i in xrange(glbv["n"]):
        for t in xrange(glbv["tn"]):
            queue2[i].b[t] = int(instance.b[i,t].value)


def stats(glbv, queue1, u1, queue2, u2):
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
    # 15 : avg_size
    # 16 : avg_wtime1_perKB(ms)
    # 17 : avg_wtime2_perKB(ms)
    # 18 : avg_wtime_perKB_decreased(ms)

    res = [0 for i in xrange(19)]

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
    res[15] = res[0]/len(queue1)
    res[16] = res[4]*1000/(res[0]/1024.0)
    res[17] = res[5]*1000/(res[0]/1024.0)
    res[18] = res[16]-res[17]

    if glbv["recall"] == 1.0:
        res[8] = 0.0

    if glbv["precision"] == 1.0:
        res[9] = 0.0

    return res


def output(glbv, res, tag="wrong"):
    """output the simulate result to console and file"""

    print "\nThis is the "+tag+" result."
    if tag == "perfect" :
        print "-------------------------------------------------------"
        print "| parameters:"
        print "| T: %d*%d, F: %d, N: %d, dis: %s" % (glbv["tn"],glbv["tl"],glbv["f"],glbv["n"],glbv["dis"])
        print "| max size: %.1f KB, min size: %.1f KB" % (glbv["maxs"]/1024.0, glbv["mins"]/1024.0)
        print "| recall : %.1f, precision: %.1f" % (glbv["recall"], glbv["precision"])
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
    print "| waiting density before schedule : %.1f ms" % res[16]
    print "| waiting density after schedule  : %.1f ms" % res[17]
    print "| waiting density decreased       : %.1f ms" % res[18]
    print "-------------------------------------------------------"


def wrt(glbv, res, res_file, sheet):
    rb = open_workbook(res_file)
    rs = rb.sheet_by_index(sheet)
    wrn = rs.nrows
    wb = copy(rb)
    ws = wb.get_sheet(sheet)

    ws.write(wrn, 0, wrn)                                   # round
    ws.write(wrn, 1, glbv["t"])                             # time
    ws.write(wrn, 2, glbv["tl"])                            # time slot
    ws.write(wrn, 3, float("%.1f" % glbv["f"]))             # frequency
    ws.write(wrn, 4, glbv["n"])                             # request
    ws.write(wrn, 5, glbv["dis"])                           # distribution
    ws.write(wrn, 6, float("%.1f" % (glbv["maxs"]/1024.0)))   # max size
    ws.write(wrn, 7, float("%.1f" % (glbv["mins"]/1024.0)))   # min size
    ws.write(wrn, 8, float("%.1f" % (res[15]/1024.0)))        # average size
    ws.write(wrn, 9, glbv["recall"])                        # recall
    ws.write(wrn, 10, glbv["precision"])                    # precision
    ws.write(wrn, 11, float("%.1f" % res[6]))               # waiting time decreased for all
    ws.write(wrn, 12, float("%.1f" % res[10]))              # waiting time decreased for hit
    ws.write(wrn, 13, float("%.1f" % res[8]))               # waiting time decreased for miss
    ws.write(wrn, 14, float("%.1f" % res[12]))              # accelerated request
    ws.write(wrn, 15, float("%.1f" % res[11]))              # decelerated request
    ws.write(wrn, 16, float("%.1f" % res[7]))               # data prefetched
    ws.write(wrn, 17, float("%.1f" % res[3]))               # finished data increase
    ws.write(wrn, 18, float("%.1f" % res[9]))               # false traffic ratio
    ws.write(wrn, 19, float("%.1f" % res[13]))              # unfinished req before schedule
    ws.write(wrn, 20, float("%.1f" % res[14]))              # unfinished req after schedule
    ws.write(wrn, 21, float("%.1f" % res[16]))              # avg_wtime1_perKB
    ws.write(wrn, 22, float("%.1f" % res[17]))              # avg_wtime2_perKB
    ws.write(wrn, 23, float("%.1f" % res[18]))              # avg_wtime_perKB_decreased

    wb.save(res_file)


def debug(glbv, q1, q2):
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
        print "r%3d,ti:%3d,Ti:%3d,Si:%7.1fKB,wt:%3d,*:%5s,si:%5.1f,wt-:%5.1f%%,ps:%5.1f%%,si+:%4.1f%%,bdt:%3d"\
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
    #        for t in xrange(prm["t"]):
    #            print "t:%3d, b:%5.1f, cb:%5.1f, db:%5.1f" % (t, r.b[t]/1024.0, q1[i].debug_b[t]/1024.0, q2[i].debug_b[t]/1024.0)
    #        pause()


def validate(glbv, q1, q2):

    equal = True
    w = 0
    e = 0
    z = 0
    p = 0

    for i,r in enumerate(q1):
        for t in xrange(glbv["tn"]):
            if r.at != q2[i].at:
                print "queue b information wrong."
                exit()

            if r.b[t] == q2[i].b[t]:
                pass
            else:
                equal = False
                #print "i:%3d t:%3d b1:%5.1f b2:%5.1f" % (i, t, r.b[t]/1024.0, q2[i].b[t]/1024.0)

    if not equal:
        for i,r in enumerate(q1):
            x = 0
            y = 0
            for t in xrange(glbv["tn"]):
                if t < r.at:
                    x += r.b[t]
                    y += q2[i].b[t]
                    w += r.b[t]
                    e += q2[i].b[t]
                z += r.b[t]
                p += q2[i].b[t]
            print i, x, y


    print "\n"
    print w,e
    print z,p

    return equal


class Request(object):
    """class for all requests"""

    def __init__(self, glbv):
        """init function"""

        ot = glbv["ot"]
        tn = glbv["tn"]

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