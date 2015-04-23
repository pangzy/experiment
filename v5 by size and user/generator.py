#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import *
from operator import itemgetter
from copy import deepcopy
from lib import load_argv
from statsmodels.distributions import ECDF
import matplotlib.pyplot as plt
import numpy as np
from math import log10


def pause():
    if raw_input("press any key to continue:"):
        pass


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
            seq.append(round(ti, 3))

    return seq


def gen_size(dim, num, s, rl):
    s1 = [[0 for j in xrange(num[i])] for i in xrange(dim)]
    d1 = [[int(round(s[i][j]*num[i])) for j in xrange(len(s[i]))] for i in xrange(dim)]

    # normalized
    for i in xrange(dim):
        if sum(d1[i]) != num[i]:
            # print "normalized."
            while sum(d1[i]) < num[i]:
                j = d1[i].index(max(d1[i]))
                d1[i][j] += 1
            while sum(d1[i]) > num[i]:
                j = d1[i].index(max(d1[i]))
                d1[i][j] -= 1

    # get size
    for i in xrange(dim):
        for j in xrange(num[i]):
            get = False
            while not get:
                a1 = choice(rl)
                a2 = rl.index(a1)
                if d1[i][a2] > 0:
                    s1[i][j] = randint(a1[0], a1[1])
                    d1[i][a2] -= 1
                    get = True

    return s1


def inverse_transform(cdf, rand, bound):
    i = bound

    while cdf(i) < rand:
        i += 1

    return i


def get_cdf():
    single_freq_file = "single_user_frequency.cdf"
    all_freq_file = "all_user_frequency.cdf"
    size_file = "traffic.cdf"

    f1 = open(single_freq_file)
    f2 = open(all_freq_file)
    f3 = open(size_file)

    lines1 = f1.readline()
    lines2 = f2.readline()
    lines3 = f3.readline()

    single_freq_sample = [int(i) for i in lines1.split(",")]
    all_freq_sample = [int(i) for i in lines2.split(",")]
    size_sample = [int(i) for i in lines3.split(",")]
    size_sample = [s/1024.0 for s in size_sample]

    single_freq_ecdf = ECDF(single_freq_sample)
    all_freq_ecdf = ECDF(all_freq_sample)
    size_ecdf = ECDF(size_sample)

    single_freq_avg = float(sum(single_freq_sample))/len(single_freq_sample)
    all_freq__avg = float(sum(all_freq_sample))/len(all_freq_sample)

    # print single_freq_avg
    # print all_freq__avg

    # print single_freq_ecdf(300)
    # print all_freq_ecdf(411)
    # print size_ecdf(10240)
    # pause()
    return all_freq_ecdf, single_freq_ecdf, size_ecdf


# generate queue from all req
def generate(gv):
    print "generate queue list."
    rc = gv["recall"]
    pc = gv["precision"]
    t = gv["time"]
    activity_dict = {"slight": 0.2, "normal": 0.5, "heavy": 0.8, "disuse": 0.0001}
    activity = [activity_dict[i] for i in gv["activity"]]

    # get time interval and scale to ms
    t = [(x[0], x[1]) for x in t]
    tn = len(t)

    # get cdf
    cdf = get_cdf()
    cdf_fa = cdf[0]
    cdf_fs = cdf[1]
    cdf_s = cdf[2]

    # get f and scale
    # f = gv["freq"]
    # f = [x for x in f]
    # generate f
    f = []
    user_num = gv["user"]
    for i in xrange(tn):
        # x = random()
        x = activity[i]
        num = inverse_transform(cdf_fs, x, 1)
        # print x, num
        num *= user_num[i]
        fi = 3600.0/num
        fi = 2.25
        f.append(fi)
    print f
    # pause()

    # q1: arrival queue, q2:miss queue, q3:false queue
    q1 = [poisson(f[i], t[i][1]-t[i][0]) for i in xrange(tn)]
    q1 = [[x+t[i][0] for x in q1[i]] for i in xrange(tn)]
    n = [len(x) for x in q1]
    q2 = [[] for i in xrange(tn)]
    q3 = [[] for i in xrange(tn)]

    # gen size from percent
    size = gv["size"]
    rl = gv["ruler"]
    s1 = gen_size(tn, n, size, rl)

    # gen size from cdf
    # s1 = [[inverse_transform(cdf_s, random(), 1024) for j in xrange(n[i])] for i in xrange(tn)]

    s2 = [[] for i in xrange(tn)]

    hit = [int(rc[i]*n[i]) for i in xrange(len(t))]
    miss = [n[i]-hit[i] for i in xrange(len(t))]
    false = [int(hit[i]*(1.0-pc[i])/pc[i]) for i in xrange(tn)]

    m_sample = [sample(range(n[i]), miss[i]) for i in xrange(tn)]
    for i in xrange(tn):
        for j in range(n[i])[::-1]:
            if j in m_sample[i]:
                q2[i].append(q1[i].pop(j))
                s2[i].append(s1[i].pop(j))

    for i in xrange(tn):
        a1 = t[i][1]-t[i][0]
        a2 = float(false[i])
        if false[i]:
            q3[i] = poisson(a1/a2, a1)
        else:
            q3[i] = []
    false = [len(q3[i]) for i in xrange(tn)]

    s3 = gen_size(tn, false, size, rl)
    # s3 = [[inverse_transform(cdf_s, random(), 1024) for j in xrange(false[i])] for i in xrange(tn)]

    q = [q1, q2, q3]
    s = [s1, s2, s3]
    queue = [[], [], []]    # queue : 0 - predict queue, 1 - arrival queue, 3 - all req queue
    flag = ("hit", "miss", "false")
    for i in xrange(3):
        for j in xrange(tn):
            for k, x in enumerate(q[i][j]):
                r = [-1, -1, -1, "none", -1]    # [idx, at, size, flag, id]
                r[1] = x
                r[2] = s[i][j][k]
                r[3] = flag[i]

                if i == 0:
                    queue[0].append(r)
                    queue[1].append(r)
                elif i == 1:
                    queue[1].append(r)
                else:
                    queue[0].append(r)
                queue[2].append(r)

    queue[0] = sorted(queue[0], key=itemgetter(1))
    queue[1] = sorted(queue[1], key=itemgetter(1))
    queue[2] = sorted(queue[2], key=itemgetter(1))

    for i, ri in enumerate(queue[2]):
        ri[0] = ri[4] = i

    for i, ri in enumerate(queue[0]):
        tmp = deepcopy(ri)
        tmp[0] = i
        queue[0][i] = tmp

    for i, ri in enumerate(queue[1]):
        tmp = deepcopy(ri)
        tmp[0] = i
        queue[1][i] = tmp

    w_lines1 = ["%s %s %s %s %s \n" % (ri[0], ri[1], ri[2], ri[3], ri[4]) for ri in queue[0]]
    w_lines2 = ["%s %s %s %s %s \n" % (ri[0], ri[1], ri[2], ri[3], ri[4]) for ri in queue[1]]
    w_lines3 = ["%s %s %s %s %s \n" % (ri[0], ri[1], ri[2], ri[3], ri[4]) for ri in queue[2]]

    wf1 = open("a.txt", "w")
    wf2 = open("b.txt", "w")
    wf3 = open("c.txt", "w")
    wf1.writelines(w_lines1)
    wf2.writelines(w_lines2)
    wf3.writelines(w_lines3)
    wf1.close()
    wf2.close()
    wf3.close()


# generate queue from multi-users
def generate2(gv):
    pass


if __name__ == '__main__':
    # gv = load_argv("arguments.conf")
    # generate(gv)
    # a = get_cdf()[2]
    # b = inverse_transform(a, 0.93993, 1024)
    # print b
    x = np.linspace(0, 100000, 100000)
    # x = [log10(i) for i in x]
    # y1 = get_cdf()[0](x)
    # plt.semilogx(x, y1)
    # y2 = get_cdf()[1](x)
    # plt.semilogx(x, y2, color="black")
    y3 = get_cdf()[2](x)
    # plt.axis([max(x)*(-0.1), max(x)*1.1, 0, 1.1])
    # plt.plot(x, y1, color="black", linewidth=1)
    # plt.plot(x, y2, color="black", linewidth=1)
    plt.semilogx(x, y3, color="black")
    plt.grid(True)
    # plt.plot(x, y3, color="black", linewidth=1)
    plt.show()



