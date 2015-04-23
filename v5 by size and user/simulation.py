#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import *
from generator import generate
from copy import deepcopy

gv = load_argv("arguments.conf")
time_length = gv["time"][-1][1] - gv["time"][0][0]
generate(gv)
q = load_queue(gv)
qa = q[0]   # predict queue
qb = q[1]   # arrival queue
qc = q[2]   # all req queue

print "predict queue length : %d" % len(qa)
print "arrival queue length : %d" % len(qb)

print "simulate arrival queue without schedule."
simulate(argv=gv, queue0=qb, scheduled=False)

print "simulate arrival queue with schedule."
simulate(argv=gv, queue0=qb, queue1=qa, scheduled=True)

print "statistics."
res = stats(queue=qb, gv=gv)

print "output."
output(gv=gv, res=res, tag="arrival queue")

print "write.\n"
log(q=qb, file="b.result")
result(res=res, gv=gv)

if __name__ == '__main__':
    pass