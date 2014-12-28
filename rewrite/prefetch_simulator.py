#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""import global module"""
from operator import itemgetter, attrgetter
from global_variable import *
from class_definition import *
import sys

"""--------------------------
generate data	: no arguments
load data		: -l

queue_a is the normal predicted request queue without prefetch schedule
queue_b is the queue after prefetch schedule
--------------------------"""
if(len(sys.argv)==1):			#generate
	dGen = ReqDataGenerator()
	dGen.genReqArrivalTime(T)
	dGen.genReqSize
	N = dGen.n
	rQueueA = []
	rQueueB = []

	for i in xrange(N):
		rQueueA.append(Request(TN))
		rQueueB.append(Request(TN))

		rQueueA[i].at   = dGen.arrivalTime[i]/TL	# ti --> timeslot_index
		rQueueA[i].size = dGen.size[i]
		rQueueA[i].left = rQueueA[i].size

		rQueueB[i].at   = rQueueA[i].at
		rQueueB[i].size = rQueueA[i].size
		rQueueB[i].left = rQueueA[i].left

elif:(sys.argv[1]=='-l'):		#load
	dLoader = ReqDataLoader(TL)
	dLoader.loadData()
	N  = dLoader.n
	T  = dLoader.t
	TN = dLoader.tn

	for i in xrange(N):
		rQueueA.append(Request(TN))
		rQueueB.append(Request(TN))

		rQueueA[i].at   = dLoader.arrivalTime[i]/TL 	# ti --> timeslot_index
		rQueueA[i].size = dLoader.size[i]
		rQueueA[i].left = rQueueA[i].size

		rQueueB[i].at   = rQueueA[i].at
		rQueueB[i].size = rQueueA[i].size
		rQueueB[i].left = rQueueA[i].left

else:
	print 'wrong argument!'
	exit()

#print 'data ok.'
print "TL:%d,TN:%d,T:%d,F:%f,N:%d,MAXS:%d KB \n" % (TL,TN,T,F,N,MAXS)

"""--------------------------------------------
simulate the process in queue A
step1.find active process
step2.simulate data transfer in current second
step3.get finished task info
--------------------------------------------"""
aReqRecorder  = []				#active req recorder
uReqRecorderA = []				#unfinished req in queue a

for t in xrange(TN):
	for r in rQueueA:
		if r.at<=t and r.left>0 and (r in aReqRecorder)==False:
			aReqRecorder.append(r)
		else:
			pass

	for r in aReqRecorder:
		if len(aReqRecorder)==0:
			break
		else:
			r.left -= (B/len(aReqRecorder))*TL

	for r in aReqRecorder:
		if r.left <= 0:
			r.ft = j
			aReqRecorder.pop(r)

"""compute waiting time and transfered data size for every req in queue A"""
for r in rQueueA:
	if r.left <= 0:
		r.wt = r.ft-r.at+1
		r.tsize = r.size
		r.left = 0
	else:
		r.ft = TN-1
		r.wt = r.ft-r.at+1
		r.tsize = r.size-r.left
		uReqRecorderA.append(r)

totalSize   = 0
totalTSizeA = 0
totalWTimeA = 0

for r in rQueueA:
	totalSize   += r.size
	totalTSizeA += r.tsize
	totalWTimeA += r.wt

print "queue A compute finished."
print "total request  data size: %d KB" % totalSize
print "total finished data size: %d KB, percent: %%%d" % (totalTSizeA,totalTSizeA*100/totalSize)
print "total waiting time:%d s" % totalWTimeA
print "unfinished req in queue a: %d\n" % len(uReqRecorderA)

"""---------------
debug information
---------------"""
for i,r in enumerate(rQueueA):
	print "r%d,ti:%d,Ti:%d,wt:%d,Si:%d,si:%d" % (i,r.at,r.ft,r.wt,r.size,r.tsize)
pause()

"""---------------------------------------
solve optimization problem,linear program
use PuLP & GPLK
---------------------------------------"""
pS = LPSolver()
pS.defProblem(rQueueA,rQueueB,N,TN)
pS.solveProblem()
pS.exportData(rQueueB,N,TN)
print "\n"

"""--------------------------------------------
simulate the process in queue B
step1.simulate data transfer in current second
step2.get finished task info
--------------------------------------------"""
for t in xrange(TN):
	for r in rQueueB:
		if r.left>0:
			r.left -= r.b[t]*TL
		else
			pass

	for r in rQueueB:
		if r.left<=0:
			if r.at>j:
				r.ft = r.at-1
			else:
				r.ft = j

"""compute waiting time and transfered data size for every req in queue B"""
totalTSizeB   = 0
totalWTimeB   = 0
totalWtSavedB = 0
reqWtSavedB	  = []
uReqRecorderB = []

for r in rQueueB:
	if left<=0:
		r.wt = r.ft-r.at+1
		r.tsize = r.size
		r.left = 0	
	else:
		r.ft = TN-1
		r.wt = r.ft-r.at+1
		r.tsize = r.size - r.left
		uReqRecorderB.append(r)

for i,r in enumerate(rQueueB):
	totalTSizeB += r.tsize
	totalWTimeB += r.wt

	tmp = rQueueA[i].wt-rQueueB[i].wt
	reqWtSavedB.append(tmp)
	totalWtSavedB += tmp

print "queue B simulation finished."
print "total finished data size:%d KB,more than queue A:%%%d" % (totalTSizeB,(totalTSizeB-totalTSizeA)*100/totalSize)
print "total waiting time saved:%d KB,less than queue A:%%%d" % (totalWtSavedB,totalWtSavedB*100/totalWTimeA)
print "total prefetching data size:%d,percent:%%%d" % (int(TL*value(pS.prob.objective)),int(TL*value(pS.prob.objective))*100/totalSize)
print "\n"

"""---------------
debug information
---------------"""
for i,r in enumerate(rQueueB):
	print "r%d,ti:%d,Ti:%d,wt_saved:%%%d,si_incr:%%%d" %\
	(i,r.at,r.ft,(rQueueA[i].wt-r.wt)*100/rQueueA[i].wt,(r.tsize-rQueueA[i].tsize)*100/totalSize)
pause()