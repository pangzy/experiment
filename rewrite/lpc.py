#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""linear problem class"""
import pulp
import math
from glv import get_glv


class LPProblem(object):
    def __init__(self):
        """init function"""
        self.glv = get_glv()
        self.tn = self.glv["tn"]
        self.n = self.glv["n"]
        self.tl = self.glv["tl"]
        self.b = self.glv["b"]

    def def_problem(self, queue_a):
        """define lp problem"""
        n = self.n
        tn = self.tn
        tl = self.tl
        b = self.b

        iIdx = range(n)
        tIdx = range(tn)
        ti = range(n)
        si = range(n)
        Ti = range(n)
        Si = range(n)

        for i in xrange(n):
            ti[i] = queue_a[i].at
            si[i] = queue_a[i].tsize
            Ti[i] = queue_a[i].ft
            Si[i] = queue_a[i].size
            iIdx[i] = str(i)

        for t in xrange(tn):
            tIdx[t] = str(t)

        """-----------------------------------
        PuLP variable definition
        varb--bi(t)
        prob--objective and constraints

        objective:
            max:[0~n-1][0~ti-1])sigma bi(t)

        constraints:
            1.any t,[0~n-1] sigma bi(t)   <= B
            2.any i,[0-Ti]  sigma bi(t)*tl>= si
            3.any i,[0~T-1] sigma bi(t)*tl<= Si
        ------------------------------------"""
        print "\ndefine lp variables"
        self.varb = pulp.LpVariable.dicts('b',(iIdx,tIdx),0,b,cat='Integer')

        print "define lp problem"
        self.prob = pulp.LpProblem('Prefetching Schedule',pulp.LpMaximize)

        print "define lp objective"
        self.prob += pulp.lpSum([tl*self.varb[i][t] for i in iIdx for t in tIdx if int(t)<ti[int(i)]])

        print "define constraints on B"
        for t in tIdx:
            self.prob += pulp.lpSum([self.varb[i][t] for i in iIdx]) <= b

        print "define constraints on si"
        for i in iIdx:
            self.prob += pulp.lpSum([tl*self.varb[i][t] for t in tIdx if int(t)<=Ti[int(i)]]) >= si[int(i)]

        print "define constraints on Si"
        for i in iIdx:
            self.prob += pulp.lpSum([tl*self.varb[i][t] for t in tIdx]) <= Si[int(i)]

    def slv_problem(self,solver="default"):
        """solve lp problem"""
        if solver == "default" or solver == "":
            print "solve lp problem using default solver."
            self.prob_status = self.prob.solve()
        elif solver == "GLPK":
            print "solve lp problem using GLPK solver."
            self.prob_status = self.prob.solve(pulp.solvers.GLPK())
        else:
            print "wrong solver argument."
            exit()

        print "Problem solved. Status: " + pulp.LpStatus[self.prob_status]

    def export_res(self,queue_b):
        n = self.n
        tn = self.tn

        for i in xrange(n):
            for t in xrange(tn):
                queue_b[i].b[t] = int(math.ceil(pulp.value(self.varb[str(i)][str(t)])))

