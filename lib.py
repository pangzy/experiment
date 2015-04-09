#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from statsmodels.distributions import ECDF
from random import *
from bisect import bisect, insort
from operator import attrgetter
from copy import deepcopy
from math import floor


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


def fmt(number):
    return round(number, 3)


def load_arguments(file_name):
    """load arguments from arguments.conf"""
    arg = {}
    cf = ConfigParser()
    cf.read(file_name)

    arg["start_time"] = cf.getint("arguments", "start_time")
    arg["time_length"] = cf.getint("arguments", "time_length")
    arg["bandwidth"] = cf.getint("arguments", "bandwidth")
    arg["out_range"] = cf.getint("arguments", "out_range")
    arg["source"] = cf.get("arguments", "source")
    arg["input"] = cf.get("arguments", "input")
    arg["output"] = cf.get("arguments", "output")

    arg["all_recall"] = cf.getfloat("prediction", "all_recall")
    arg["all_precision"] = cf.getfloat("prediction", "all_precision")
    arg["text_recall"] = cf.getfloat("prediction", "text_recall")
    arg["text_precision"] = cf.getfloat("prediction", "text_precision")
    arg["image_recall"] = cf.getfloat("prediction", "image_recall")
    arg["image_precision"] = cf.getfloat("prediction", "image_precision")
    arg["app_recall"] = cf.getfloat("prediction", "app_recall")
    arg["app_precision"] = cf.getfloat("prediction", "video_precision")
    arg["video_recall"] = cf.getfloat("prediction", "video_recall")
    arg["video_precision"] = cf.getfloat("prediction", "all_precision")
    arg["audio_recall"] = cf.getfloat("prediction", "audio_recall")
    arg["audio_precision"] = cf.getfloat("prediction", "audio_precision")
    arg["other_recall"] = cf.getfloat("prediction", "other_recall")
    arg["other_precision"] = cf.getfloat("prediction", "other_precision")

    return arg


def load_queue(q_file):
    q_list = [[], [], []]

    for i, file_i in enumerate(q_file):
        fp = open(file_i)
        while 1:
            line = fp.readline()
            if not line:
                break
            ls = line.split()
            r = Req()
            r.at = fmt(float(ls[1]))
            r.size = int(ls[2])
            r.flag = ls[3]
            r.id = int(ls[4])
            r.left = r.size
            r.data = r.size
            q_list[i].append(r)

    return q_list


def stat_sample():
    # {"10B": 0, "100B": 0, "1KB": 0, "10KB": 0, "100KB": 0, "1MB": 0, "10MB": 0, "100MB": 0, "1GB": 0}
    # size_basket = [0 for i in xrange(100*1000*1000)]    # 10B per basket in 1GB, 100000000 baskets
    file_list = ("26_4.dat", "27_4.dat", "28_4.dat")
    x_index = {"text": 0, "image": 1, "application": 2, "video": 3, "audio": 4, "other": 5, "all": 6}
    length = [[] for i in xrange(7)]
    freq = [[0 for j in xrange(24)] for i in xrange(7)]
    bound = (10, 100, 1024, 10*1024, 100*1024, 1024*1024, 10*1024*1024, 100*1024*1024, 1024*1024*1024)
    basket = []
    for fn in file_list:
        f = open(fn)
        while 1:
            line = f.readline()
            if not line:
                break
            ls = line.split()
            h = int(ls[0][3:5])
            m = int(ls[0][6:8])
            s = int(ls[0][9:11])
            if ls[2].isdigit():
                length[6].append(int(ls[2]))
                length[x_index[ls[1]]].append(int(ls[2]))
                freq[6][h] += 1
                freq[x_index[ls[1]]][h] += 1

    for i in xrange(7):
        ecdf = ECDF(length[i])
        basket.append(ecdf(bound))

    for i in xrange(7):
        for j in xrange(24):
            if freq[i][j] == 0:
                freq[i][j] = 7200.0
            else:
                freq[i][j] = 3600.0 / freq[i][j]

    return basket, freq


def poisson(f, bound):
    """generate a integer sequence under poisson distribution"""
    lamda = 1.0/f
    ti = 0.0
    seq = []
    while True:
        ti += expovariate(lamda)
        if int(ti) >= bound:
            break
        else:
            seq.append(fmt(ti))

    return seq


'''
def generate(arg, basket, freq, clock=24, method="all"):
    """-----------------------------------------
    hit+miss = arrived

    recall = hit/arrived = hit/(hit+miss)
    precise = hit/N = hit/(hit+false) = (N-f)/N

    hit:miss  = recall :(1-recall) ,recall>0
    hit:false = precise:(1-precise),precise>0
    -----------------------------------------"""
    size_bound = (10, 100, 1024, 10*1024, 100*1024, 1024*1024, 10*1024*1024, 100*1024*1024, 1024*1024*1024)
    recall = (arg["text_recall"], arg["image_recall"], arg["app_recall"],arg["video_recall"], arg["audio_recall"], arg["other_recall"], arg["all_recall"])
    precision = (arg["text_precision"], arg["image_precision"], arg["app_precision"],arg["video_precision"], arg["audio_precision"], arg["other_precision"], arg["all_precision"])

    # arrival
    q1 = [[poisson(freq[i][j], 3600) for j in xrange(clock)] for i in xrange(7)]
    hit = [[int(recall[i]*len(q1[i][j])) for j in xrange(clock)] for i in xrange(7)]

    # miss
    miss = [[int((1.0-recall[i])*len(q1[i][j])) for j in xrange(clock)] for i in xrange(7)]
    miss_sample = [[sample(xrange(len(q1[i][j])), miss[i][j]) for j in xrange(clock)] for i in xrange(7)]
    # print miss[0][0], miss[1][0],miss[2][0],miss[3][0],miss[4][0],miss[5][0],miss[6][0]
    q2 = [[[] for j in xrange(clock)] for i in xrange(7)]
    for i in xrange(7):
        for j in xrange(clock):
            for k in range(len(q1[i][j]))[::-1]:
                if k in miss_sample[i][j]:
                    q2[i][j].append(q1[i][j].pop(k))

    # false
    false = [[int(((1.0-precision[i])/precision[i])*hit[i][j]) for j in xrange(clock)] for i in xrange(7)]
    q3 = [[[] for j in xrange(clock)] for i in xrange(7)]
    for i in xrange(7):
        for j in xrange(clock):
            if false[i][j] != 0:
                q3[i][j] = poisson(3600.0/false[i][j], 3600)

    # arrival_queue
    q = [q1, q2, q3]
    # queue[0], queue[2] : predict queue (hit + false), queue[1], queue[3] : submitted queue
    # queue[0], queue[1] : generate req for every type, queue[2], queue[3] : generate req for all type
    queue = [[[] for j in xrange(clock)] for i in xrange(4)]
    for j in xrange(clock):
        for i in xrange(7):
            for n in xrange(3):
                for k in q[n][i][j]:
                    r = Req(arg)
                    # arrival time
                    r.at = 3600.0*j + k
                    # size
                    rand1 = random()
                    idx = bisect(basket[i], rand1)
                    if idx == 0:
                        lower = 1
                        upper = size_bound[0]
                    else:
                        lower = size_bound[idx-1]
                        upper = size_bound[idx]
                    r.size = randint(lower, upper)
                    r.left = r.size
                    r.data = r.size
                    # type
                    r.type = i
                    # flag
                    if n == 0:
                        r.flag = "hit"
                    elif n == 1:
                        r.flag = "miss"
                    else:
                        r.flag = "false"
                    # join queue
                    if i == 6:  # all
                        if r.flag != "miss":
                            queue[2][j].append(r)
                            r.id[0] = j
                            r.id[1] = queue[2][j].index(r)
                        queue[3][j].append(r)
                    else:   # type
                        if r.flag != "miss":
                            queue[0][j].append(r)
                            r.id[0] = j
                            r.id[1] = queue[0][j].index(r)
                        queue[1][j].append(r)

        for p in xrange(4):
            queue[p][j] = sorted(queue[p][j], key=attrgetter("at"))

    if method == "all":
        return queue[2], queue[3]
    else:
        return queue[0], queue[1]
'''


def simulate(s_list=None, **kwargs):
    arg = kwargs["arg"]
    q = kwargs["queue"]
    scheduled = kwargs["scheduled"]
    # print s_list
    b = arg["bandwidth"]
    ot = arg["out_range"]
    b_avl = b
    timer = []
    n_req = []
    f_req = []
    test = []
    ms = fmt(0.001)
    t = [0.0, 0.0]
    inf = 24*3600.0

    if not scheduled:
        for r in q:
            timer.append(r.at)

        i = 0
        j = 0
        while 1:
            t[0] = timer[j]
            # print "t[0]:%f" % t[0]
            if j < len(timer)-1:
                t[1] = timer[j+1]
            else:
                t[1] = inf
            new = False
            # print "t[1]:%f" % t[1]

            for r in q:
                if r.at <= t[0] and r.left > 0 and (r not in n_req):
                    n_req.append(r)

            if n_req:
                b_avg = b / len(n_req)
                for n in n_req:
                    dt = fmt(n.left/b_avg)
                    dt = max(dt, ms)
                    if t[0] + dt < t[1]:
                        t[1] = t[0]+dt
                        new = True

                if new:
                    insort(timer, t[1])
                    # print "t[1]:%f" % t[1]
                    # print "download: %f" % (b_avg*(t[1]-t[0]))

                for n in n_req[::-1]:
                    n.left -= b_avg*fmt(t[1]-t[0])
                    if n.left <= 0:
                        n.left = 0
                        n.ft = t[1]
                        n.wt = fmt(n.ft - n.at)
                        n_req.pop(n_req.index(n))
                        i += 1
                        # print "i:%d" % i
                        # print "wt:%f" % n.wt

            if i >= len(q):
                break

            j += 1
            # print "j:%d" % j
            # pause()
    else:
        timer = [0.0]
        for r in q:
            if r.flag == "miss":
                timer.append(r.at)

        sl = deepcopy(s_list)

        i = 0
        j = 0
        # s = 0
        while 1:
            t[0] = timer[j]
            if j < len(timer)-1:
                t[1] = timer[j+1]
            else:
                t[1] = inf
            new = False

            for u in sl:
                if q[u].flag == "miss":
                    print "schedule list wrong."
                    exit()

            for r in q:
                if r.at <= t[0] and r.data > 0 and r.flag == "miss" and (r not in n_req):
                    n_req.append(r)
                    r.st = r.at
                    test.append(q.index(r))
                    #print "miss req"
                    #print [q.index(ccc) for ccc in n_req]

            if (not n_req) and sl:
                # print "scheduled req"
                # print "id in C: %d" % sl[0]
                n_req.append(q[sl[0]])
                test.append(sl[0])
                q[sl[0]].st = t[0]
                sl.pop(0)

                #print [q.index(ccc) for ccc in n_req]
                #pause()

            if n_req:
                b_avg = b / len(n_req)
                for n in n_req:
                    dt = fmt(n.data/b_avg)
                    dt = max(dt, ms)
                    if fmt(t[0]+dt) < t[1]:
                        t[1] = fmt(t[0]+dt)
                        new = True

                if new:
                    insort(timer, t[1])

                for n in n_req[::-1]:
                    data = b_avg*fmt(t[1]-t[0])
                    n.data -= data
                    if t[1] <= n.at:
                        n.ps += data
                    elif t[0] < n.at:
                        n.ps += b_avg*fmt(n.at-t[0])
                    else:
                        pass

                    if n.ps > n.size:
                        n.ps = n.size

                    if n.data <= 0:
                        n.data = 0
                        n.et = t[1]
                        if n.et <= n.at:
                            n.lt = 0.0
                        else:
                            n.lt = fmt(n.et-n.at)
                        n_req.pop(n_req.index(n))
                        f_req.append(q.index(n))
                        # print q.index(n)
                        # print n.st, n.et
                        # print i
                        # pause()

                        i += 1

            if i >= len(q):
                #print test
                #pause()
                break

            j += 1

    for x in q:
        if (x.ft == ot and not scheduled) or (x.et == ot and scheduled):
            print "there is task unfinished."
            print q.index(x)
            print "simulate."
            # exit()


def merge(l):
    for i in range(len(l))[:0:-1]:
        if l[i][0] == l[i-1][1]:
            l[i-1] = [l[i-1][0], l[i][1]]
            l.pop(i)


def add_zone(l, idx, sub):
    ms = fmt(0.001)
    if sub[0] < l[idx][0] or sub[1] > l[idx][1]:
        print "add idle zone error."
        exit()

    if fmt(l[idx][1]-l[idx][0]) < ms:
        print "idle zone too small."

        print l[idx][1]
        print l[idx][0]

        exit()

    if sub[0] == l[idx][0] and sub[1] == l[idx][1]:
        l.pop(idx)
    elif sub[0] == l[idx][0] and sub[1] < l[idx][1]:
        l[idx][0] = fmt(sub[1])
    elif sub[0] > l[idx][0] and sub[1] == l[idx][1]:
        l[idx][1] = fmt(sub[0])
    elif sub[0] > l[idx][0] and sub[1] < l[idx][1]:
        tmp = l[idx][0]
        l[idx][0] = fmt(sub[1])
        l.insert(idx, [fmt(tmp), fmt(sub[0])])


def adjust(l):
    l.sort()
    for i in range(len(l))[:0:-1]:
        if l[i][0] < l[i-1][1]:
            print "task zone conflict."
            exit()

    for i in range(len(l))[:0:-1]:
        for j in range(i)[::-1]:
            if j < 0 or j >= len(l):
                print "jjj: %d" % j
                print len(l)
                pause()

            if i < 0 or i >= len(l):
                print "iii: %d" % i
                print len(l)
                pause()

            if l[j][2] == l[i][2] != -1:
                j_len = fmt(l[j][1]-l[j][0])
                l[i][0] = fmt(l[i][0]) - j_len
                for k in xrange(j+1, i):
                    l[k][0] = fmt(l[k][0]) - j_len
                    l[k][1] = fmt(l[k][1]) - j_len
                l[j][2] = -1

    for i in range(len(l))[::-1]:
        if l[i][2] == -1:
            l.pop(i)

    # print l


def schedule(arg, queue, **kwargs):
    arg = arg
    q = queue
    start_time = arg["start_time"]
    time_length = arg["time_length"]
    b = arg["bandwidth"]
    ot = arg["out_range"]
    ms = fmt(0.001)
    q = sorted(q, key=attrgetter("ft"))
    slot_end = kwargs["slot_end"]

    idle = [[0.0, float(slot_end)]]
    task = []
    s_list = []

    for i, r in enumerate(q):
        tail = fmt(r.at)
        length = fmt(float(r.data)/b)
        length = max(length, ms)
        head = fmt(tail-length)
        body = [head, tail]
        while length > 0:
            # print i
            # print length
            # print "find a idle zone"
            # find a idle zone
            idx = ot
            fwd = True
            for j in xrange(len(idle)):
                if idle[j][0] < body[1]:
                    idx = j
                    fwd = True

            if idx == ot:
                for j in range(len(idle))[::-1]:
                    if idle[j][0] >= body[1]:
                        idx = j
                        fwd = False

            if idx == ot:
                print "not enough bandwidth."
                exit()
            # print "place & cut"
            # place & cut
            if fwd:
                tail = fmt(min(body[1], idle[idx][1]))
                head = fmt(max((tail-length), idle[idx][0]))
                if fmt(tail-head) < fmt(length):
                    # length -= (tail-head)
                    length = fmt(length) - fmt(tail-head)
                    body[1] = head
                    body[0] = body[1]-length
                else:
                    length = 0.0
            else:
                head = fmt(idle[idx][0])
                tail = fmt(min((head+length), idle[idx][1]))
                if fmt(tail-head) < fmt(length):
                    length = fmt(length) - fmt(tail-head)
                    body[0] = tail
                    body[1] = body[0]+length
                else:
                    length = 0.0

            if head >= r.ft:
                print r.id, r.at, head, tail, r.size
                print idle
                pause()

            # cut idle zone
            # print "head: %f" % head
            # print "tail: %f" % tail
            task.append([head, tail, r.id])
            add_zone(idle, idx, [head, tail])
            # print idle
            # pause()

        # merge idle zone
        merge(idle)

    # adjust task zone
    adjust(task)

    # get schedule list
    for x in task:
        s_list.append(x[2])

    # print s_list

    return s_list


def schedule2(queue):
    q = sorted(queue, key=attrgetter("ft"))
    s_list = [r.id for r in q]

    return s_list


def simulate2(s_list=None, **kwargs):
    arg = kwargs["arg"]
    q = kwargs["queue"]
    scheduled = kwargs["scheduled"]
    # print s_list
    b = arg["bandwidth"]
    ot = arg["out_range"]
    b_avl = b
    timer = []
    n_req = []
    ms = fmt(0.001)
    t = [0.0, 0.0]
    inf = 24*3600.0

    if not scheduled:
        for r in q:
            timer.append(r.at)

        i = 0
        j = 0
        while 1:
            t[0] = timer[j]
            # print "t[0]:%f" % t[0]
            if j < len(timer)-1:
                t[1] = timer[j+1]
            else:
                t[1] = inf
            new = False
            # print "t[1]:%f" % t[1]

            for r in q:
                if r.at <= t[0] and r.left > 0 and (r not in n_req):
                    n_req.append(r)

            if n_req:
                b_avg = b / len(n_req)
                for n in n_req:
                    dt = fmt(n.left/b_avg)
                    dt = max(dt, ms)
                    if t[0] + dt < t[1]:
                        t[1] = t[0]+dt
                        new = True

                if new:
                    insort(timer, t[1])
                    # print "t[1]:%f" % t[1]
                    # print "download: %f" % (b_avg*(t[1]-t[0]))

                for n in n_req[::-1]:
                    n.left -= b_avg*fmt(t[1]-t[0])
                    if n.left <= 0:
                        n.left = 0
                        n.ft = t[1]
                        n.wt = fmt(n.ft - n.at)
                        n_req.pop(n_req.index(n))
                        i += 1
                        # print "i:%d" % i
                        # print "wt:%f" % n.wt

            if i >= len(q):
                break

            j += 1
            # print "j:%d" % j
            # pause()
    else:
        # timer = [0.0]
        timer = [r.at for r in q]
        timer.insert(0, 0.0)
        sl = deepcopy(s_list)
        # timer1 = [0.0]
        # for r in q:
        #     if r.flag == "miss":
        #         timer.append(r.at)
        #     else:
        #         timer1.append(r.at)

        i = 0
        j = 0
        s = 0
        while 1:
            t[0] = timer[j]
            if j < len(timer)-1:
                t[1] = timer[j+1]
            else:
                t[1] = inf
            new = False

            for r in q:
                if r.at <= t[0] and r.data > 0 and (r not in n_req):
                    n_req.append(r)
                    r.st = r.at
                    if q.index(r) in sl:
                        sl.pop(sl.index(q.index(r)))

            if (not n_req) and sl:
                n_req.append(q[sl[0]])
                q[sl[0]].st = t[0]
                sl.pop(0)

            if n_req:
                b_avg = b / len(n_req)
                for n in n_req:
                    dt = fmt(n.data/b_avg)
                    dt = max(dt, ms)
                    if fmt(t[0]+dt) < t[1]:
                        t[1] = fmt(t[0]+dt)
                        new = True

                if new:
                    insort(timer, t[1])

                for n in n_req[::-1]:
                    data = b_avg*fmt(t[1]-t[0])
                    n.data -= data
                    if t[1] <= n.at:
                        n.ps += data
                    elif t[0] < n.at:
                        n.ps += b_avg*fmt(n.at-t[0])
                    else:
                        pass

                    if n.ps > n.size:
                        n.ps = n.size

                    if n.data <= 0:
                        n.data = 0
                        n.et = t[1]
                        if n.et <= n.at:
                            n.lt = 0.0
                        else:
                            n.lt = fmt(n.et-n.at)
                        n_req.pop(n_req.index(n))
                        i += 1

            if i >= len(q):
                break

            j += 1

    for x in q:
        if (x.ft == ot and not scheduled) or (x.et == ot and scheduled):
            print "there is task unfinished."
            print q.index(x)
            print "simulate2."
            #exit()


def simulate3(s_list=None, **kwargs):
    arg = kwargs["arg"]
    q = kwargs["queue"]
    scheduled = kwargs["scheduled"]
    b = arg["bandwidth"]
    ot = arg["out_range"]
    timer = []
    n_req = []
    p_req = None
    ms = fmt(0.001)
    t = [0.0, 0.0]
    inf = 24*3600.0

    if not scheduled:
        for r in q:
            timer.append(r.at)

        i = 0
        j = 0
        while 1:
            t[0] = timer[j]
            if j < len(timer)-1:
                t[1] = timer[j+1]
            else:
                t[1] = inf
            new = False

            for r in q:
                if r.at <= t[0] and r.left > 0 and (r not in n_req):
                    n_req.append(r)

            if n_req:
                b_avg = b / len(n_req)
                for n in n_req:
                    dt = fmt(n.left/b_avg)
                    dt = max(dt, ms)
                    if t[0] + dt < t[1]:
                        t[1] = t[0]+dt
                        new = True

                if new:
                    insort(timer, t[1])

                for n in n_req[::-1]:
                    n.left -= b_avg*fmt(t[1]-t[0])
                    if n.left <= 0:
                        n.left = 0
                        n.ft = t[1]
                        n.wt = fmt(n.ft - n.at)
                        n_req.pop(n_req.index(n))
                        i += 1

            if i >= len(q):
                break

            j += 1
    else:
        timer = [r.at for r in q]
        timer.insert(0, 0.0)
        sl = deepcopy(s_list)

        i = 0
        j = 0
        while 1:
            t[0] = timer[j]
            if j < len(timer)-1:
                t[1] = timer[j+1]
            else:
                t[1] = inf
            new = False
            mark = False

            for r in q:
                if r.at <= t[0] and r.data > 0 and (r not in n_req):
                    if r is p_req:
                        p_req = None
                    else:
                        r.st = r.at
                    n_req.append(r)
                    if q.index(r) in sl:
                        sl.pop(sl.index(q.index(r)))
                    mark = True

            if (not n_req) and (not p_req) and sl:
                p_req = q[sl[0]]
                q[sl[0]].st = t[0]
                sl.pop(0)
                mark = True

            if n_req:
                b_avg = b / len(n_req)
                for n in n_req:
                    dt = fmt(n.data/b_avg)
                    dt = max(dt, ms)
                    if fmt(t[0]+dt) < t[1]:
                        t[1] = fmt(t[0]+dt)
                        new = True

                if new:
                    insort(timer, t[1])

                for n in n_req[::-1]:
                    data = b_avg*fmt(t[1]-t[0])
                    n.data -= data

                    if n.data <= 0:
                        n.data = 0
                        n.et = t[1]
                        n.lt = fmt(n.et-n.at)
                        n_req.pop(n_req.index(n))
                        i += 1

            elif p_req:
                dt = fmt(p_req.data/b)
                dt = max(dt, ms)
                if fmt(t[0]+dt) < t[1]:
                    t[1] = fmt(t[0]+dt)
                    insort(timer, t[1])

                data = b*fmt(t[1]-t[0])
                p_req.data -= data
                p_req.ps += data

                if p_req.ps > p_req.size:
                    p_req.ps = p_req.size

                if p_req.data <= 0:
                    p_req.data = 0
                    p_req.et = t[1]
                    p_req.lt = 0.0
                    # timer.pop(timer.index(p_req.at))
                    p_req = None
                    i += 1

            else:
                pass
                # print p_req
                # print n_req
                # print t[0], t[1]
                # print i
                # print len(q)
                # print len(timer)
                # print mark
                # print sl
                # print "schedule bug."
                # exit()


            if i >= len(q):
                break

            j += 1

    for x in q:
        if (x.ft == ot and not scheduled) or (x.et == ot and scheduled):
            print "there is task unfinished."
            print q.index(x)
            print "simulate3."
            #exit()


def get_slot(q):
    q = sorted(q, key=attrgetter("ft"))
    slot_end = q[-1].ft
    q = sorted(q, key=attrgetter("at"))
    return slot_end

'''
def transfer(s_list, qc, qa, arg):
    ot = arg["out_range"]

    for r in qc:
        if r.flag == "miss" and r.id != ot:
            print "index error in queue C."
            exit()

    for i, s in enumerate(s_list):
        for j, r in enumerate(qc):
            if r.id == s:
                s_list[i] = j
'''


def transfer(qb, qc):
    for r in qb:
        for x in qc:
            if r.id == x.id:
                r.st = x.st
                r.et = x.et
                r.lt = x.lt
                r.ps = x.ps


def stats(**kwargs):
    q = kwargs["queue"]

    res = {"s": 0, "psp": 0.0, "fsp": 0.0, "wtd": 0.0, "wtd_e": 0.0, "rde": 0.0, "rac": 0.0, "ruc": 0.0}
    wt1 = wt2 = wt3 = wt4 = 0.0

    for i, r in enumerate(q):
        res["s"] += r.size
        res["psp"] += r.ps
        wt1 += r.wt
        wt2 += r.lt

        if r.flag == "false":
            res["fsp"] += r.size
        else:
            wt3 += r.wt
            wt4 += r.lt

        if (r.wt - r.lt) > 0:
            res["rac"] += 1
        elif (r.wt - r.lt) < 0:
            res["rde"] += 1
        else:
            res["ruc"] += 1
            # print i, r.wt, r.lt
            # print r.at, r.ft, r.st, r.et
            # print r.flag, r.size
            # pause()

    res["psp"] = res["psp"]*100.0/res["s"]
    res["fsp"] = res["fsp"]*100.0/res["s"]
    res["wtd"] = (wt1-wt2)*100.0/wt1
    res["wtd_e"] = (wt3-wt4)*100.0/wt3
    res["rde"] = res["rde"]*100.0/len(q)
    res["rac"] = res["rac"]*100.0/len(q)
    res["ruc"] = res["ruc"]*100.0/len(q)

    return res


def output(**kwargs):
    arg = kwargs["arg"]
    res = kwargs["res"]
    tag = kwargs["tag"]

    st = kwargs["st"]
    et = kwargs["et"]
    sh = st / 3600
    eh = et / 3600
    sm = (st - sh*3600) / 60
    em = (et - eh*3600) / 60

    print "\nThis is the "+tag+" result."
    print "-------------------------------------------------------"
    print "| parameters:"
    print "| Slot: %s:%s ~ %s:%s" % (str(sh).zfill(2), str(sm).zfill(2), str(eh).zfill(2), str(em).zfill(2))
    print "| recall: %.1f, precision: %.1f" % (arg["all_recall"], arg["all_precision"])
    print "-------------------------------------------------------"
    print "| waiting time decreased for all  : %.1f%%" % res["wtd"]
    print "| waiting time decreased for user : %.1f%%" % res["wtd_e"]
    print "| accelerated request             : %.1f%%" % res["rac"]
    print "| decelerated request             : %.1f%%" % res["rde"]
    print "| unchanged   request             : %.1f%%" % res["ruc"]
    print "| data prefetched                 : %.1f%%" % res["psp"]
    print "| false traffic percent           : %.1f%%" % res["fsp"]
    print "-------------------------------------------------------"


def wrt(**kwargs):
    wf = open(kwargs["file"], "w")
    q = kwargs["q"]

    lines = "id  r.size  r.at     r.ft    r.wt    r.st    r.et    r.lt    r.flag    ac/de \n"
    for r in q:
        lines = lines + str(r.id) + "\t" + str(r.size/1024).zfill(4) + "\t" + str(r.at).zfill(6) + "\t" + str(r.ft).zfill(6) + "\t" + \
                str(r.wt).zfill(6) + "\t" + str(r.st).zfill(6) + "\t" + str(r.et).zfill(6) + "\t" + str(r.lt).zfill(6) + "\t" + r.flag + "\t\t"

        if r.wt > r.lt:
            lines = lines + "fast" + "\n"
        elif r.wt < r.lt:
            lines = lines + "slow" + "\n"
        else:
            lines = lines + "hold" + "\n"

    wf.writelines(lines)
    wf.close()


if __name__ == '__main__':
    # a = load_arguments("arguments.conf")
    # b = stat_sample()[0]
    # f = stat_sample()[1]
    # generate(a, b, f)
    a = [[3, 4], [5, 6], [6, 7], [8, 9], [9, 10]]
    merge(a)
    print a