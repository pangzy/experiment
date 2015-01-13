#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xlrd import *
# from xlwt import *
from xlutils.copy import copy
from pulp import *
from random import *
from operator import attrgetter
from copy import deepcopy
from math import ceil
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
        glbv["path"] = "D:\Experiment\prefetching-simulation\project\plan_b\\"
        glbv["config_file"] = glbv["path"]+"glbv.xlsx"
    elif platform.system() == "Linux":
        glbv["path"] = "/home/pangzy/virtualenv/test_1/test"
        glbv["config_file"] = glbv["path"]+"/glbv.xlsx"

    xls = open_workbook(glbv["config_file"])
    table = xls.sheet_by_index(0)

    for i in xrange(table.nrows):
        glbv[table.cell(i, 0).value] = table.cell(i, 1).value

    for k, v in glbv.iteritems():
        if isinstance(v, float) and k != "recall" and k != "precision":
            glbv[k] = int(v)

    glbv["t"] = glbv["tn"]*glbv["tl"]
    glbv["n"] = glbv["t"]/glbv["f"]

    if platform.system() == "Windows":
        glbv["data_file"] = glbv["path"]+glbv["data1"]
        glbv["result_file"] = glbv["path"]+glbv["result1"]
    elif platform.system() == "Linux":
        glbv["data_file"] = glbv["path"]+"/"+glbv["data1"]
        glbv["result_file"] = glbv["path"]+"/"+glbv["result1"]

    return glbv


def rdm_poi(glbv):
    """generate a integer sequence under poisson distribution"""
    lamda = 1.0/glbv["f"]
    ti = 0.0
    seq = []
    while True:
        ti += expovariate(lamda)
        if int(ti) >= glbv["t"]:
            break
        else:
            seq.append(int(ti))

    return seq


def rdm_uni(glbv, n, use):
    """generate a integer sequence under uniform random distribution"""
    seq = []
    if use == "time":
        seq = [randint(0, glbv["t"]-1) for i in xrange(n)]
        seq.sort()
    elif use == "size":
        seq = [randint(glbv["mins"], glbv["maxs"]) for i in xrange(n)]
    else:
        print "need a 'use' argument for generate uniform data."
        exit()

    return seq


def gen_base(glbv):
    """generate arrival queue"""

    queue = []
    time_seq = []
    size_seq = []
    if glbv["dis"] == "poisson":
        time_seq = rdm_poi(glbv)
        glbv["n"] = len(time_seq)
        size_seq = rdm_uni(glbv, glbv["n"], "size")
    elif glbv["dis"] == "uniform":
        time_seq = rdm_uni(glbv, glbv["n"], "time")
        size_seq = rdm_uni(glbv, glbv["n"], "size")
    else:
        print "need an argument for data distribution."
        exit()

    for i in xrange(glbv["n"]):
        queue.append(Request(glbv))
        queue[i].at = time_seq[i]/glbv["tl"]
        queue[i].size = size_seq[i]
        queue[i].left = queue[i].size

    return queue


def load_base(glbv, pos):
    """load arrival queue from .xls"""

    print "loading data..."

    rfile = glbv["data_file"]
    sheet_index = pos[0]
    time_col = pos[1]
    size_col = pos[2]
    start_row = pos[3]
    end_row = pos[4]

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


def gen_deviation(queue, glbv, accuracy=(1.0, 1.0)):
    """generate deviation data
       input: arrival queue
       output: predicted(hit+false) queue, submitted(hit+false+miss) queue, arrival(hit+miss) queue
    """

    recall = accuracy[0]
    precision = accuracy[1]
    hit = int(recall*glbv["n"])
    miss = glbv["n"]-hit
    false = int(((1.0-precision)/precision)*hit)

    # false queue
    f_queue = []
    time_seq = rdm_uni(glbv, false, "time")
    size_seq = rdm_uni(glbv, false, "size")
    for i in xrange(false):
        f_queue.append(Request(glbv))
        f_queue[i].at = time_seq[i]/glbv["tl"]
        f_queue[i].size = size_seq[i]
        f_queue[i].left = f_queue[i].size
        f_queue[i].flag = "false"

    # arrival queue
    for i in sample(xrange(len(queue)), miss):
        queue[i].flag = "miss"

    a_queue = deepcopy(queue)

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

    p_queue = deepcopy(queue)

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


def simulate(glbv, queue, scheduled=False, perfect=True):
    """simulate request events"""
    tn = glbv["tn"]
    tl = glbv["tl"]
    B = glbv["b"]
    ot = glbv["ot"]
    ureq_recorder = []

    if not scheduled:
        nreq_recorder = []
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

    return ureq_recorder


def schedule(glbv, queue1, queue2):
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


    if accuracy == (1.0, 1.0):
        res[8] = 0.0
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


def simulate_fcfs(glbv, queue):
    tn = glbv["tn"]
    tl = glbv["tl"]
    B = glbv["b"]
    ot = glbv["ot"]
    ureq_recorder = []

    preq_recorder = []
    nreq_recorder = []

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

                if r.at > t and r not in preq_recorder:
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