#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lib
import copy


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

q_list = lib.gen_extra(base, args, accuracy)

a = q_list[0]  # predicted queue
b = copy.deepcopy(a)
args["n"] = len(a)

print "simulate perfect queue before schedule."
unfinished_a = lib.simulate(args, a)

print "schedule perfect queue."
lib.schedule(args, a, b)

print "\nsimulate perfect queue after schedule."
unfinished_b = lib.simulate(args, b, True)

c = q_list[1]  # submitted queue
d = copy.deepcopy(c)
lib.inh_data(d, b, args)

print "simulate imperfect queue before schedule."
unfinished_c = lib.simulate(args, c)

print "simulate imperfect queue after schedule."
unfinished_d = lib.simulate(args, d, True)

print "statistics."
res_perfect = lib.stats(a, unfinished_a, b, unfinished_b)
res_imperfect = lib.stats(c, unfinished_c, d, unfinished_d, accuracy)

print "output."

print "simulation finished."
