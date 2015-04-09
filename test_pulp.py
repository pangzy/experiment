#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pulp import *
from random import *
from math import ceil
from pyomo.environ import *
from pyomo.opt import SolverFactory


def schedule_pulp():
    at = [randint(0, 100) for i in xrange(10)]
    num = len(at)
    size = [randint(5, 30) for i in xrange(num)]
    wt = [randint(1, 6) for i in xrange(num)]
    idx = [str(i) for i in xrange(num)]
    sst = [0 for i in xrange(num)]

    st = LpVariable.dicts("st", idx, 0, 100, cat="Integer")

    prob = LpProblem("test", LpMinimize)

    x = [st[i]+size[int(i)]/10-at[int(i)] for i in idx if st[i]+size[int(i)]/10-at[int(i)]>0]

    prob += lpSum([st[i]+size[int(i)]/10-at[int(i)] for i in idx if st[i]+size[int(i)]/10-at[int(i)] > 0])

    for i in idx:
        prob += st[i]+size[int(i)]/10-at[int(i)] <= wt[int(i)]

    prob_status = prob.solve()
    print LpStatus[prob_status]
    for i in xrange(num):
        sst[i] = int(ceil(value(st[str(i)])))

    print prob.objective
    print value(prob.objective)
    print at
    print size
    print wt
    print sst


def schedule_pyomo():
    num = 10

    at = [randint(0, 100) for i in xrange(num)]
    length = [randint(2, 5) for i in xrange(num)]
    wt = [randint(1, 6) for i in xrange(num)]

    model = AbstractModel("schedule")
    model.n = Param(default=num)
    model.i = RangeSet(0, model.n-1)
    model.st = Var(model.i, domain=NonNegativeIntegers, bounds=(0, model.n-1))
    et = [model.st[i]+length[i] for i in xrange(num)]
    lt = [max(et[i]-at[i], 0) for i in xrange(num)]

    # def obj_rule(model, length, at, num):
    def obj_rule(model):
    # a = [[length[model.rank[x]] for x in xrange(i)] for i in xrange(num)]
    # st = [sum(a[i]) for i in xrange(num)]
    # et = [st[i]+length[i] for i in xrange(num)]
    # lt = [max(et[i]-at[i], 0) for i in xrange(num)]
    # return lt
        return sum([max((model.st[i]+length[i]-at[i]), 0) for i in xrange(10)])
    model.obj = Objective(rule=obj_rule, sense=minimize)


    def c1_rule(model, j):
        # a = [[length[model.rank[x]] for x in xrange(i)] for i in xrange(num)]
        # st = [sum(a[i]) for i in xrange(num)]
        return lt[j] - wt[j] <= 0

    model.c1 = Constraint(model.i, rule=c1_rule)

    opt = SolverFactory("glpk")
    instance = model.create()
    result = opt.solve(instance)
    instance.load(result)
    print result.solution[0].status


if __name__ == '__main__':
    # schedule_pulp()
    schedule_pyomo()
