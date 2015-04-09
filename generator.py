#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from random import *
from operator import itemgetter
from copy import deepcopy


def pause():
    if raw_input("press any key to continue:"):
        pass


def fmt(number):
    return round(number, 3)


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


def generate(t_len, freq):
    print "generate queue list."

    recall = 0.7
    precision = 0.7

    q1 = poisson(freq, t_len)
    q2 = []
    q3 = []

    hit = int(recall*len(q1))
    miss = len(q1) - hit
    false = int((1.0-precision)/precision*hit)

    m_sample = sample(range(len(q1)), miss)
    for i in range(len(q1))[::-1]:
        if i in m_sample:
            q2.append(q1.pop(i))

    if false:
        q3 = poisson(t_len/false, t_len)

    q = [q1, q2, q3]
    queue = [[], [], []]
    size = (1024*16, 1024*128, 1024*1024)
    flag = ("hit", "miss", "false")
    for i in xrange(3):
        for j in q[i]:
            r = [0, 0.0, 0, "hit", -1]       # [idx, at, size, flag, id]
            r[1] = j
            r[2] = choice(size)
            r[3] = flag[i]

            if r[3] == "hit":
                queue[0].append(r)
                queue[1].append(r)
                queue[2].append(r)
            elif r[3] == "miss":
                queue[1].append(r)
                queue[2].append(r)
            else:
                queue[0].append(r)
                queue[2].append(r)

            # if r[3] != "miss":
            #    queue[0].append(r)
            # queue[1].append(r)

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


if __name__ == '__main__':
    generate(200, 2.5)
