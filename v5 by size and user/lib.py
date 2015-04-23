#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from bisect import insort
# from math import floor


class Req(object):
    def __init__(self):
        ot = -1

        self.at = ot
        self.ft = ot
        self.wt = ot
        self.st = ot
        self.et = ot
        self.lt = ot
        self.id = ot
        self.size = 0
        self.data = 0
        self.ps = 0
        self.flag = "hit"
        # self.b = 0
        self.left = 0
        self.type = ot


def pause():
    if raw_input("press any key to continue:"):
        pass


def load_argv(file_name):
    gv = {}
    cf = ConfigParser()
    cf.read(file_name)

    # time interval
    t = cf.get("arguments", "time_interval")
    t = t.split(",")
    for i, x in enumerate(t):
        x = x.split("~")
        t[i] = (int(x[0]), int(x[1]))
    gv["time"] = t

    # freq
    '''
    f = cf.get("arguments", "freq")
    f = f.split(",")
    f = [int(x) for x in f]
    if len(f) != len(t):
        print "<freq> argument wrong."
        exit()
    gv["freq"] = f
    '''
    # size
    s = cf.get("arguments", "size")
    s = s.split(";")
    s = [x.split(",") for x in s]
    s = [[float(y) for y in x] for x in s]
    if len(s) != len(t):
        print "<size> arguments wrong."
        exit()
    for x in s:
        if round(sum(x), 1) != 1.0:
            print "<size> arguments not normalized."
            exit()
    gv["size"] = s

    # size ruler (KB)
    # gv["ruler"] = [(1, 10), (10, 100), (100, 1024), (1024, 10240), (10240, 102400), (102400, 1048576)]
    gv["ruler"] = [(1, 10), (10, 100), (100, 1024), (1024, 1024), (10240, 102400), (102400, 1048576)]

    # recall & precision
    rc = cf.get("prediction", "recall")
    pc = cf.get("prediction", "precision")
    rc = rc.split(",")
    rc = [float(x) for x in rc]
    pc = pc.split(",")
    pc = [float(x) for x in pc]
    if len(rc) != len(t) or len(pc) != len(t):
        print "<recall/precision> arguments wrong."
        exit()
    gv["recall"] = rc
    gv["precision"] = pc

    # other
    gv["bandwidth"] = cf.getint("arguments", "bandwidth")
    gv["ot"] = cf.getint("arguments", "out_range")
    u = cf.get("arguments", "user_number")
    u = u.split(",")
    u = [int(x) for x in u]
    gv["user"] = u
    ac = cf.get("arguments", "activity")
    gv["activity"] = ac.split(",")

    return gv


def load_queue(gv):
    fl = ("a.txt", "b.txt", "c.txt")
    q = [[], [], []]

    for i, fi in enumerate(fl):
        fp = open(fi)
        lines = fp.readlines()
        for line in lines:
            ls = line.split()
            r = Req()
            r.at = round(float(ls[1]), 3)
            r.size = int(ls[2])
            r.flag = ls[3]
            r.id = int(ls[4])
            r.left = r.size
            r.data = r.size
            q[i].append(r)

        '''
        while 1:
            line = fp.readline()
            if not line:
                break
            ls = line.split()
            r = Req()
            r.at = round(float(ls[1]), 3)
            r.size = int(ls[2])
            r.flag = ls[3]
            r.id = int(ls[4])
            r.left = r.size
            r.data = r.size
            q[i].append(r)
        '''

    return q


def simulate(**kwargs):
    gv = kwargs["argv"]
    q0 = kwargs["queue0"]
    scheduled = kwargs["scheduled"]
    # set b in Bps
    b = gv["bandwidth"]
    ot = gv["ot"]
    nq = []
    ms = round(0.001, 3)
    t = [0.0, 0.0]
    inf = 24*3600.0

    if not scheduled:
        timer = [r.at for r in q0]

        rp = 0
        tp = 0
        while 1:
            t[0] = timer[tp]
            if tp < len(timer)-1:
                t[1] = round(timer[tp+1], 3)
            else:
                t[1] = inf

            for r in q0:
                if r.at <= t[0] and r.left > 0 and (r not in nq):
                    nq.append(r)

            if nq:
                b_avg = float(b) / len(nq)
                # b_avg = round(b_avg)
                # b_avg = floor(b_avg)
                # b_avg = max(b_avg, b*ms)
                for r in nq:
                    dt = r.left / b_avg
                    dt = round(dt+0.00045, 3)       # ceil from .3f
                    dt = max(dt, ms)
                    if round(t[0]+dt, 3) < round(t[1], 3):
                        t[1] = round(t[0]+dt, 3)

                if t[1] not in timer:
                    insort(timer, t[1])

                for r in nq[::-1]:
                    r.left -= b_avg*round(t[1]-t[0], 3)
                    if r.left <= 0:
                        r.left = 0
                        r.ft = t[1]
                        r.wt = round(r.ft-r.at, 3)
                        nq.pop(nq.index(r))
                        rp += 1

            if rp >= len(q0):
                break

            tp += 1

    else:
        q1 = kwargs["queue1"]
        nq_id = []
        pr = None
        q0_id = [r.id for r in q0]
        q1_id = [r.id for r in q1]
        timer = [r.at for r in q0]
        timer.insert(0, 0.0)
        rp = 0
        tp = 0

        while 1:
            t[0] = timer[tp]
            if tp < len(timer)-1:
                t[1] = round(timer[tp+1], 3)
            else:
                t[1] = inf

            # task pr from prefetch to normal
            if pr and pr.at <= t[0]:
                if pr.id in q0_id:
                    idx_q0 = q0_id.index(pr.id)
                    q0[idx_q0].st = pr.st
                    q0[idx_q0].data = pr.data
                    q0[idx_q0].ps = pr.ps
                pr = None

            # arrival request
            for r in q0:
                if r.at <= t[0] and r.data > 0 and (r not in nq):
                    nq.append(r)

                    if r.st == ot:      # not prefetched
                        r.st = t[0]

                    if r.id in q1_id:       # hit but not prefetched
                        idx_q1 = q1_id.index(r.id)
                        r.ps = 0
                        r.st = t[0]
                        q1.pop(idx_q1)
                        q1_id.pop(idx_q1)

            # remove false req in q1
            for r in q1[::-1]:
                if r.at <= t[0]:
                    q1.pop(q1.index(r))
                    q1_id.pop(q1_id.index(r.id))

            # start a prefetch when idle
            if (not nq) and (not pr) and q1:
                pr = q1.pop(0)
                q1_id.pop(0)
                pr.st = t[0]

            if nq:
                b_avg = float(b) / len(nq)
                # b_avg = round(b_avg)
                # b_avg = floor(b_avg)
                # b_avg = max(b_avg, 1.0)
                for r in nq:
                    dt = r.data / b_avg
                    dt = round(dt+0.00045, 3)
                    dt = max(dt, ms)
                    if round(t[0]+dt, 3) < round(t[1], 3):
                        t[1] = round(t[0]+dt, 3)

                if t[1] not in timer:
                    insort(timer, t[1])

                for r in nq[::-1]:
                    r.data -= b_avg*round(t[1]-t[0], 3)
                    if r.data <= 0:
                        r.data = 0
                        r.et = t[1]
                        r.lt = round(r.et-r.at, 3)
                        nq.pop(nq.index(r))
                        rp += 1
            elif pr:
                dt = float(pr.data) / b
                dt = round(dt+0.00045, 3)
                dt = max(dt, ms)
                point = round(t[0]+dt, 3)       # prefetch end time
                t[1] = min(point, pr.at, t[1])
                t[1] = round(t[1], 3)
                if t[1] not in timer:
                    insort(timer, t[1])

                pr.data -= b*round(t[1]-t[0], 3)
                pr.ps += b*round(t[1]-t[0], 3)
                pr.ps = min(pr.ps, pr.size)

                if pr.data <= 0:
                    if pr.id in q0_id:      # hit
                        idx_q0 = q0_id.index(pr.id)
                        if q0[idx_q0].data == 0:
                            print "prefetch process error."
                            print q0[idx_q0].id
                            exit()
                        else:
                            q0[idx_q0].data = 0
                            q0[idx_q0].st = pr.st
                            q0[idx_q0].et = t[1]
                            q0[idx_q0].lt = 0.0
                            q0[idx_q0].ps = pr.ps
                            rp += 1

                    pr = None

                    #for r in q0:
                    #    if r.id == pr.id:
                    #        if r.data == 0:
                    #            print "prefetch process error."
                    #            print r.id
                    #            exit()
                    #        else:
                    #            r.data = 0
                    #            r.et = t[1]
                    #            r.lt = 0.0
                    #            r.ps = pr.ps
                    #            rp += 1

            if rp >= len(q0):
                break

            tp += 1

    for x in q0:
        if (x.ft == ot and (not scheduled)) or (x.et == ot and scheduled):
            print "there is task unfinished."
            print q0.index(x)
            exit()


def stats(**kwargs):
    q = kwargs["queue"]
    gv = kwargs["gv"]

    res = {"s": 0, "psp": 0.0, "fsp": 0.0, "wtd": 0.0, "wtd_e": 0.0, "rde": 0.0, "rac": 0.0, "ruc": 0.0,
           "edge": 0.0, "vol": 0.0, "idle": 0.0}
    wt1 = wt2 = 0.0

    for i, r in enumerate(q):
        res["s"] += r.size
        res["psp"] += r.ps
        wt1 += r.wt
        wt2 += r.lt

        if (r.wt - r.lt) > 0:
            res["rac"] += 1
        elif (r.wt - r.lt) < 0:
            res["rde"] += 1
        else:
            res["ruc"] += 1

    res["psp"] = res["psp"]/res["s"]
    res["wtd"] = (wt1-wt2)*100.0/wt1
    res["rde"] = res["rde"]*100.0/len(q)
    res["rac"] = res["rac"]*100.0/len(q)
    res["ruc"] = res["ruc"]*100.0/len(q)
    res["edge"] = max([r.ft for r in q])
    res["vol"] = gv["bandwidth"]*res["edge"]
    res["idle"] = (res["vol"]-res["s"])/res["s"]
    res["pir"] = res["psp"] / res["idle"]
    # latency_per_object_ratio
    res["lpor"] = wt2*100.0 / wt1
    # average latency without prefetch
    res["alnp"] = float(wt1)/len(q)
    # average latency with prefetch
    res["alyp"] = float(wt2)/len(q)
    # average size per req
    res["avgs"] = float(res["s"])/len(q)
    # average arrival interval per req
    res["avgi"] = q[-1].at/len(q)
    # average traffic
    res["avgtf"] = float(res["s"])/q[-1].at
    return res


def output(**kwargs):
    gv = kwargs["gv"]
    res = kwargs["res"]
    tag = kwargs["tag"]

    print "\nThis is the "+tag+" result."
    print "-------------------------------------------------------"
    print "| parameters:"
    print "| recall: %s, precision: %s" % (gv["recall"], gv["precision"])
    print "-------------------------------------------------------"
    # print "| latency per object ratio        : %.1f%%" % res["lpor"]
    print "| waiting time decreased          : %.1f%%" % res["wtd"]
    print "| average latency (no prefetch)   : %.3f s" % round(res["alnp"], 3)
    print "| average latency (prefetch)      : %.3f s" % round(res["alyp"], 3)
    print "| accelerated request             : %.1f%%" % res["rac"]
    print "| decelerated request             : %.1f%%" % res["rde"]
    print "| unchanged   request             : %.1f%%" % res["ruc"]
    print "| prefetched data                 : %.1f%%" % (res["psp"]*100.0)
    print "| total data                      : %.1f" % res["s"]
    print "| average size per req            : %.1f" % res["avgs"]
    print "| average interval per req        : %.1f" % res["avgi"]
    print "| average traffic                 : %.1f" % res["avgtf"]
    print "-------------------------------------------------------"


def log(**kwargs):
    wf = open(kwargs["file"], "w")
    q = kwargs["q"]

    lines = "id   size      at         ft          wt           st          et          lt      flag  ac/de  pf\n"
    for r in q:
        lines = lines + str(r.id) + "\t" + str(r.size).zfill(4) + "\t" + str(r.at).zfill(8) + "\t" + str(r.ft).zfill(8) + "\t" + \
                str(r.wt).zfill(8) + "\t" + str(r.st).zfill(8) + "\t" + str(r.et).zfill(8) + "\t" + str(r.lt).zfill(8) + "\t" + r.flag[0] + "      "

        if r.wt > r.lt:
            lines = lines + "f" + "\t"
        elif r.wt < r.lt:
            lines = lines + "s" + "\t"
            lines = lines + "s" + "\t"
        else:
            lines = lines + "h" + "\t"

        a1 = r.ps / r.size
        a1 = round(a1, 2)
        a1 = str(a1)
        if r.ps:
            lines = lines + "y" + "\n"
        else:
            lines = lines + "n" + "\n"

    wf.writelines(lines)
    wf.close()


def result(**kwargs):
    wf = open("result.dat", "a")

    res = kwargs["res"]
    gv = kwargs["gv"]

    lines = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\n".format(str(gv["time"]),
                                                                              str(gv["user"]),
                                                                              str(gv["activity"]),
                                                                              str(gv["recall"]),
                                                                              str(gv["precision"]),
                                                                              str(round(res["wtd"], 1)),
                                                                              str(round(res["psp"] * 100.0, 1)),
                                                                              str(round(res["rac"], 1)),
                                                                              str(round(res["avgs"], 1)),
                                                                              str(round(res["avgi"], 1)),
                                                                              str(round(res["avgtf"], 1)))
    wf.writelines(lines)
    wf.close()


if __name__ == '__main__':
    load_argv("arguments.conf")