#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lib
import copy
import pulp


args = lib.load_args()

pos = (args["sheet_index"],args["time_col"],args["size_col"],args["start_row"],args["end_row"])
accuracy = (args["recall"],args["precision"])
base = []

if args["source"] == "g":
    print "\ngenerate base data."
    base = lib.gen_base(args)
elif args["source"] == "l":
    print "\nload base data."
    base = lib.load_base(args, pos)
elif args["source"] == "r":
    pass
else:
    print "data source argument wrong."
    exit()

print "generate deviation data."
q_list = lib.gen_extra(base, args, accuracy)

a = q_list[0]  # predicted queue
b = copy.deepcopy(a)
args["n"] = len(a)

print "simulate perfect queue before schedule."
unfinished_a = lib.simulate(args, a, scheduled=False, perfect=True)

print "schedule perfect queue."
v = lib.schedule(args, a, b)

print "\nsimulate perfect queue after schedule."
unfinished_b = lib.simulate(args, b, scheduled=True, perfect=True)

c = q_list[1]  # submitted queue
d = copy.deepcopy(c)
lib.inh_data(d, b, args)

print "simulate imperfect queue before schedule."
unfinished_c = lib.simulate(args, c, scheduled=False, perfect=False)

print "simulate imperfect queue after schedule."
unfinished_d = lib.simulate(args, d, scheduled=True, perfect=False)

res_perfect = lib.stats(a, unfinished_a, b, unfinished_b)
res_imperfect = lib.stats(c, unfinished_c, d, unfinished_d, accuracy)

#lib.output(args, res_perfect, "perfect")
#lib.output(args, res_imperfect, "imperfect")

lib.debug(args, a, b)
lib.debug(args, c, d)

print "------------------"
print "| abnormal request"
print "------------------"
for i,r in enumerate(b):
    if a[i].wt-r.wt < 0:
        print "r%3d" % i
        for t in xrange(args["t"]):
            print "t:%3d, b:%5.1f, ab:%5.1f, bb:%5.1f, cb:%5.1f, db:%5.1f" % \
                  (t, r.b[t], a[i].debug_b[t], b[i].debug_b[t],
                   c[i].debug_b[t]/1024.0, d[i].debug_b[t]/1024.0)

        x = 0
        y = 0.0
        for t in xrange(args['t']):
            x += r.debug_b[t]
            y += pulp.value(v[str(i)][str(t)])

        print "x: %d, y: %.1f, Si: %d, si:%d, a_si:%d" % (x, y, r.size, r.gsize, a[i].gsize)

        lib.pause()

print "\nsimulation finished."
