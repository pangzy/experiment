#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import *
from copy import deepcopy
# from pulp import *

glbv = load_glbv()
base = []

if glbv["source"] == "g":
    print "\ngenerate base data."
    base = gen_base(glbv)
elif glbv["source"] == "l":
    print "\nload base data."
    base = load_base(glbv)
elif glbv["source"] == "r":
    pass
else:
    print "data source argument wrong."
    exit()

print "generate deviation data."
q_list = gen_deviation(base, glbv)

a = q_list[0]  # predicted queue
glbv["n"] = len(a)
b = clone_queue(glbv, a)
a_fcfs = clone_queue(glbv, a)

print "\nsimulate predict queue without schedule in plan [optimize]."
unfinished_a = simulate(glbv, a, q_type="a")

# schedule_pyomo(glbv, a, b)
schedule_pulp(glbv, a, b)

print "\nsimulate predict queue with schedule in plan [optimize]."
unfinished_b = simulate(glbv, b, q_type="b")

print "simulate predict queue with schedule in plan [fcfs]."
unfinished_a_fcfs = simulate(glbv, a_fcfs, q_type="fcfs")

c = q_list[1]  # submitted queue
d = clone_queue(glbv, c)
c_fcfs = clone_queue(glbv, c)
# c_fcfs = deepcopy(c)
inh_data(d, b, glbv)

print "\nsimulate evaluation queue without schedule in plan [optimize]."
unfinished_c = simulate(glbv, c, q_type="c")

print "simulate evaluation queue with schedule in plan [optimize]."
unfinished_d = simulate(glbv, d, q_type="d")

print "simulate evaluation queue with schedule in plan [fcfs]."
unfinished_c_fcfs = simulate(glbv, c_fcfs, q_type="fcfs")

print "\nprocess result."
res_pq = stats(glbv, a, unfinished_a, b, unfinished_b)
res_eq = stats(glbv, c, unfinished_c, d, unfinished_d)

res_fcfs_pq = stats(glbv, a, unfinished_a, a_fcfs, unfinished_a_fcfs)
res_fcfs_eq = stats(glbv, c, unfinished_c, c_fcfs, unfinished_c_fcfs)

output(glbv, res_pq, "predicted queue")
output(glbv, res_eq, "evaluation queue")

output(glbv, res_fcfs_pq, "fcfs predicted queue")
output(glbv, res_fcfs_eq, "fcfs evaluation queue")

if glbv["wrt"] == "y":
    wrt(glbv, res_pq, glbv["result_file"], 1)
    wrt(glbv, res_eq, glbv["result_file"], 2)
    wrt(glbv, res_fcfs_pq, glbv["result_file"], 3)
    wrt(glbv, res_fcfs_eq, glbv["result_file"], 4)


# debug(glbv, a, b)
# debug(glbv, c, d)

# debug(glbv, a, tmp_b)
# debug(glbv, c, tmp_d)

# print "\n\n"
# tmp_res_perfect = stats(a, unfinished_a, tmp_b, tmp_unfinished_b)
#t mp_res_imperfect = stats(c, unfinished_c, tmp_d, tmp_unfinished_d, accuracy)

# output(glbv, tmp_res_perfect, "perfect")
# output(glbv, tmp_res_imperfect, "imperfect")

'''
print "------------------"
print "| abnormal request"
print "------------------"
for i,r in enumerate(d):
    if c[i].wt-r.wt < 0:
        print "r%3d" % i
        for t in xrange(glbv["tn"]):
            print "t:%3d, b:%5.1f, ab:%5.1f, bb:%5.1f, cb:%5.1f, db:%5.1f" % \
                  (t, r.b[t]/1024.0, a[i].debug_b[t]/1024.0, b[i].debug_b[t]/1024.0,
                   c[i].debug_b[t]/1024.0, d[i].debug_b[t]/1024.0)

        x = 0
        y = 0.0
        for t in xrange(glbv['tn']):
            x += r.debug_b[t]

        print "x: %d, Si: %d, si:%d, a_si:%d" % (x, r.size, r.gsize, a[i].gsize)

        pause()
'''
print "\nsimulation finished."

