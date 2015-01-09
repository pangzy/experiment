#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pyomo.environ import *
from pyomo.opt import SolverFactory
from lib import *
from copy import deepcopy
# from pulp import *


glbv = load_glbv()

pos = (glbv["sheet_index"], glbv["time_col"], glbv["size_col"], glbv["start_row"], glbv["end_row"])
accuracy = (glbv["recall"], glbv["precision"])
base = []

if glbv["source"] == "g":
    print "\ngenerate base data."
    base = gen_base(glbv)
elif glbv["source"] == "l":
    print "\nload base data."
    base = load_base(glbv, pos)
elif glbv["source"] == "r":
    pass
else:
    print "data source argument wrong."
    exit()

print "generate deviation data."
q_list = gen_deviation(base, glbv, accuracy)

a = q_list[0]  # predicted queue
b = deepcopy(a)
glbv["n"] = len(a)
# tmp_b = deepcopy(b)

print "simulate perfect queue before schedule."
unfinished_a = simulate(glbv, a, scheduled=False, perfect=True)

print "schedule perfect queue."
ti = [r.at for r in a]
si = [r.gsize for r in a]
Ti = [r.ft for r in a]
Si = [r.size for r in a]

model = AbstractModel("schedule")
model.n = Param(default=glbv["n"])
model.T = Param(default=glbv["tn"])
model.B = Param(default=glbv["b"])
model.tl = Param(default=glbv["tl"])
model.i = RangeSet(0, model.n-1)
model.t = RangeSet(0, model.T-1)

print "define var."
model.b = Var(model.i, model.t, domain=NonNegativeIntegers, bounds=(0, model.B))

print "define obj."
def obj_rule(model):
    return sum(model.tl*model.b[i,t] for i in xrange(model.n) for t in xrange(ti[i]))
model.obj = Objective(rule=obj_rule, sense=maximize)

print "define constraints."
def c1_rule(model, t):
    return sum(model.b[i,t] for i in xrange(model.n)) <= model.B
model.c1 = Constraint(model.t, rule=c1_rule)

def c2_rule(model, i):
    return sum(model.tl*model.b[i,t] for t in xrange(Ti[i]+1)) >= si[i]
model.c2 = Constraint(model.i, rule=c2_rule)

def c3_rule(model, i):
    return sum(model.tl*model.b[i,t] for t in xrange(model.T)) <= Si[i]
model.c3 = Constraint(model.i, rule=c3_rule)

print "solve problem."
opt = SolverFactory("glpk")
instance = model.create()
result = opt.solve(instance)
instance.load(result)

print "\n%d solution found in pyomo." % len(result.solution)
for i,r in enumerate(result.solution):
    print "  solution %d : %s" % (i+1, r.status)

for i in xrange(glbv["n"]):
    for t in xrange(glbv["tn"]):
        b[i].b[t] = int(instance.b[i,t].value)

# v = schedule(glbv, a, tmp_b)

# print result.solution[0].objective
# print "pulp"
# print pulp.value(v[1])

# pause()

# validate(glbv, b, tmp_b)

# pause()

print "\nsimulate perfect queue after schedule."
unfinished_b = simulate(glbv, b, scheduled=True, perfect=True)
# tmp_unfinished_b = simulate(glbv, tmp_b, scheduled=True, perfect=True)

c = q_list[1]  # submitted queue
d = deepcopy(c)
inh_data(d, b, glbv)

# tmp_d = deepcopy(c)
# inh_data(tmp_d, tmp_b, glbv)

print "simulate imperfect queue before schedule."
unfinished_c = simulate(glbv, c, scheduled=False, perfect=False)

print "simulate imperfect queue after schedule."
unfinished_d = simulate(glbv, d, scheduled=True, perfect=False)
# tmp_unfinished_d = simulate(glbv, tmp_d, scheduled=True, perfect=False)

res_perfect = stats(a, unfinished_a, b, unfinished_b)
res_imperfect = stats(c, unfinished_c, d, unfinished_d, accuracy)

output(glbv, res_perfect, "perfect")
output(glbv, res_imperfect, "imperfect")

if glbv["wrt"] == "y":
    wrt(glbv, res_perfect, glbv["result1"], 1)
    wrt(glbv, res_imperfect, glbv["result1"], 2)


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

