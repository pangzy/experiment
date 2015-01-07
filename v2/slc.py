#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""simulation class"""
import glv
import xlrd
import xlwt
import random
import operator
import lpc
import dpc



def pause():
    """pause for debug"""
    if raw_input("press any key to continue:"):
        pass


class Request(object):
    """class for all requests"""

    def __init__(self):
        """init function"""
        self.glv = glv.get_glv()
        ot = self.glv["ot"]
        tn = self.glv["tn"]

        self.at = ot                # arrival time
        self.ft = ot                # finish time
        self.wt = ot                # waiting time
        self.size = 0               # req data size
        self.tsize = 0              # data size of req got in [0,T]
        self.psize = 0              # prefetched size
        self.left = 0               # left size
        self.flag = "hit"           # req category flag : miss,false,hit
        self.bdt = ot               # bdp,boundary timepoint
        self.b = range(tn)          # bandwidth for ri at timeslot t in queue_b
        self.debug_b = range(tn)

        for t in xrange(tn):
            self.b[t] = 0
            self.debug_b[t] = 0


class Queue(object):
    """class for all request queues"""

    def __init__(self):
        """init function"""
        self.queue = []
        self.glv = glv.get_glv()
        self.tl = self.glv["tl"]
        self.tn = self.glv["tn"]
        self.t = self.glv["t"]
        self.f = self.glv["f"]
        self.n = self.glv["n"]
        self.maxs = self.glv["maxs"]
        self.mins = self.glv["mins"]

    def gen_queue(self, dis="poisson"):
        """generate queue data"""
        dg = dpc.DataGenerator()

        if dis == "poisson":
            dg.gen_poisson(self.t)
            dg.get_time()
            dg.gen_uniform(self.n, self.t, "size")
            dg.get_size()
            glv.set_n(dg.n)
            self.n = glv.get_glv()["n"]
        elif dis == "uniform" or dis == "":
            dg.gen_uniform(self.n, self.t, "time")
            dg.get_time()
            dg.gen_uniform(self.n, self.t, "size")
            dg.get_size()
        else:
            pass

        for i in xrange(self.n):
            self.queue.append(Request())
            self.queue[i].at = dg.time[i] / self.tl
            self.queue[i].size = dg.size[i]
            self.queue[i].left = self.queue[i].size

    def load_queue(self, pos):
        dl = dpc.DataLoader()
        dl.load(position=pos)

        glv.set_n(dl.n)
        glv.set_t(dl.t)
        glv.set_tn(dl.tn)
        glv.set_f(dl.t / dl.n)

        self.n = glv.get_glv()["n"]
        self.t = glv.get_glv()["t"]
        self.tn = glv.get_glv()["tn"]
        self.f = glv.get_glv()["f"]

        for i in xrange(self.n):
            self.queue.append(Request())
            self.queue[i].at = dl.time[i] / self.tl
            self.queue[i].size = dl.size[i]
            self.queue[i].left = self.queue[i].size

    def read_queue(self):
        """read queue data from file"""
        pass

    def inh_queue(self, q):
        """inherit self from q"""
        for i in xrange(len(q)):
            self.queue.append(Request())
            self.queue[i].at = q[i].at
            self.queue[i].size = q[i].size
            self.queue[i].bdt = q[i].ft
            self.queue[i].left = self.queue[i].size
            self.queue[i].flag = q[i].flag

            for t in xrange(self.tn):
                self.queue[i].b[t] = q[i].b[t]

    def mix_queue(self, recall, precise):
        hit = int(precise * self.n)
        false = self.n - hit
        miss = int(((1.0 - recall) / recall) * hit)
        queue_m = []

        dg = dpc.DataGenerator()

        dg.gen_uniform(miss, self.t,"time")
        dg.get_time()
        dg.gen_uniform(miss, self.t,"size")
        dg.get_size()

        for i in xrange(miss):
            queue_m.append(Request())
            queue_m[i].at = dg.time[i] / self.tl
            queue_m[i].size = dg.size[i]
            queue_m[i].left = queue_m[i].size
            queue_m[i].flag = "miss"

        for i in random.sample(range(self.n), false):
            self.queue[i].flag = "false"

        self.queue.extend(queue_m)
        self.queue = sorted(self.queue, key=operator.attrgetter("at"))

    def wrt_queue(self):
        """write queue data to a xls file"""
        pass

    def draw_queue(self):
        """draw queue chart"""
        pass


class Simulator(object):
    """class for simulation process"""

    def __init__(self):
        """init function"""
        self.glv = glv.get_glv()
        self.tl = self.glv["tl"]
        self.tn = self.glv["tn"]
        self.t = self.glv["t"]
        self.f = self.glv["f"]
        self.n = self.glv["n"]
        self.b = self.glv["b"]
        self.ot = self.glv["ot"]
        self.maxs = self.glv["maxs"]
        self.mins = self.glv["mins"]

    def process(self, queue, with_schedule=False):
        """main()"""
        tn = self.tn
        tl = self.tl
        n = self.n
        B = self.b
        ot = self.ot
        sta_total_size = 0
        sta_total_tsize = 0
        sta_total_wtime = 0
        sta_total_psize = 0
        sta_false_wtime = 0
        sta_false_psize = 0
        sta_miss_wtime = 0

        if not with_schedule:
            nreq_recorder = []
            ureq_recorder = []
            for t in xrange(tn):
                for r in queue:
                    if r.at <= t and r.left > 0 and (r not in nreq_recorder):
                        nreq_recorder.append(r)
                    else:
                        pass

                if len(nreq_recorder) == 0:
                    pass
                else:
                    for r in nreq_recorder:
                        r.left -= (B / len(nreq_recorder)) * tl
                        r.debug_b[t] = B / len(nreq_recorder)

                for r in nreq_recorder[::-1]:
                    if r.left <= 0:
                        r.ft = t
                        nreq_recorder.pop(nreq_recorder.index(r))
                    else:
                        pass

            for i, r in enumerate(queue):
                if r.left <= 0:
                    r.wt = r.ft - r.at + 1
                    r.tsize = r.size
                    r.left = 0
                else:
                    r.ft = tn - 1
                    r.wt = r.ft - r.at + 1
                    r.tsize = r.size - r.left
                    ureq_recorder.append(r)

            for r in queue:
                sta_total_size += r.size
                sta_total_tsize += r.tsize
                sta_total_wtime += r.wt

        else:  # if with_schedule==False:
            preq_recorder = []
            nreq_recorder = []
            ureq_recorder = []
            mreq_recorder = []
            xreq_recorder = []

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
                        else:
                            pass
                    else:
                        pass

            for r in preq_recorder[::-1]:
                if r.at <= t:
                    nreq_recorder.append(preq_recorder.pop(preq_recorder.index(r)))
                    continue
                else:
                    pass

                if len(mreq_recorder) == 0:
                    r.left -= r.b[t] * tl
                    r.psize += r.b[t] * tl
                    r.debug_b = r.b[t]
                else:
                    pass

            for r in nreq_recorder[::-1]:
                if r.bdt < t:
                    mreq_recorder.append(nreq_recorder.pop(nreq_recorder.index(r)))
                    continue
                else:
                    pass

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
                    else:
                        pass
                else:
                    pass

        for r in queue:
            if r.left <= 0:
                r.wt = r.ft - r.at + 1
                r.tsize = r.size
                r.left = 0
            else:
                r.ft = tn - 1
                r.wt = r.ft - r.at + 1
                r.tsize = r.size - r.left
                ureq_recorder.append(r)

        for i, r in enumerate(queue):
            sta_total_size += r.size
            sta_total_tsize += r.tsize
            sta_total_wtime += r.wt
            sta_total_psize += r.psize

            if r.flag == "miss":
                sta_miss_wtime += r.wt
            elif r.flag == "false":
                sta_false_wtime += r.wt
                sta_false_psize += r.psize
            else:
                pass

    def solve(self, queue_a, queue_b, solver=""):
        lp = lpc.LPProblem()
        lp.def_problem(queue_a)
        lp.slv_problem(solver)
        lp.export_res(queue_b)

    def evaluation(self):
        pass

    def prt_sta(self):
        pass

    def draw_chart(self):
        pass