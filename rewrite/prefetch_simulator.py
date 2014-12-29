#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""import global module"""
from operator import itemgetter, attrgetter
from random import sample
from copy import deepcopy
from global_variable import *
from class_definition import *
from xlwt import *
import sys

"""---------------------------------------------------------------------------------------
args: data source: -g/-l [lp solver: ""/GLPK] [arrival time distribution: poisson/uniform]

queue A is the normal predicted request queue without prefetch schedule
queue B is the queue after prefetch schedule
queue C is the evaluation queue with miss and false
queue D is the evaluation queue with miss and false but without schedule
---------------------------------------------------------------------------------------"""
if len(sys.argv)==1:
	print "need more arguments"
	print "args: '<data source>' ('<lp solver>' '<data gen distribution>' )"
	exit()
else:
	pass

if sys.argv[1]== "-g" :			#generate
	if len(sys.argv)>=4 and sys.argv[3]=="uniform":
		dGen = ReqDataGenerator()
		dGen.genReqArrivalTime(N,T,dis="uniform")
		dGen.genReqSize(N,dis="uniform")
	else:
		dGen = ReqDataGenerator()
		dGen.genReqArrivalTime(N,T)
		N = dGen.n
		dGen.genReqSize(N)	

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

elif sys.argv[1]=='-l' :		#load
	dLoader = ReqDataLoader(TL)
	dLoader.loadData()
	N  = dLoader.n
	T  = dLoader.t
	TN = dLoader.tn
	F  = T/N

	for i in xrange(N):
		rQueueA.append(Request(TN))
		rQueueB.append(Request(TN))

		rQueueA[i].at   = dLoader.arrivalTime[i]/TL 	# ti --> timeslot_index
		rQueueA[i].size = dLoader.size[i]
		rQueueA[i].left = rQueueA[i].size

		rQueueB[i].at   = rQueueA[i].at
		rQueueB[i].size = rQueueA[i].size
		rQueueB[i].left = rQueueA[i].left

else :
	print 'wrong argument!'
	exit()

print "\nTL:%d,TN:%d,T:%d,F:%.1f,N:%d,MAXS:%d KB \n" % (TL,TN,T,F,N,MAXS)

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

	if len(aReqRecorder)==0:
		pass
	else:
		for r in aReqRecorder:
			r.left -= (B/len(aReqRecorder))*TL	

	for r in aReqRecorder[::-1]:
		if r.left <= 0:
			r.ft = t
			aReqRecorder.pop(aReqRecorder.index(r))
		else:
			pass

"""compute waiting time and transfered data size for every req in queue A"""

for i,r in enumerate(rQueueA):
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

print "queue A (%d req) compute finished." % len(rQueueA)
print "unfinished req in queue A: %d" % len(uReqRecorderA)
print "total request  data size: [%d KB]" % totalSize
print "total finished data size: [%d KB], percent: [%%%.1f]" % (totalTSizeA,totalTSizeA*100.0/totalSize)
print "total waiting time: [%d s]\n" % totalWTimeA

"""---------------
debug information

for i,r in enumerate(rQueueA):
	print "r%3d, ti:%3d, Ti:%3d, wt:%3d, Si:%5d, si:%5d, left:%5d" % (i,r.at,r.ft,r.wt,r.size,r.tsize,r.left)
pause()
---------------"""

"""---------------------------------------
solve optimization problem,linear program
use PuLP & GPLK
---------------------------------------"""
if len(sys.argv)<3:
	solver = ""
else:
	solver = sys.argv[2]

pS = LPSolver()
pS.defProblem(rQueueA,rQueueB,N,TN)
pS.solveProblem(solver)
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
		else:
			pass

	for r in rQueueB:
		if r.left<=0 and r.ft == OT:
			if r.at>t:
				r.ft = r.at-1
			else:
				r.ft = t
		else:
			pass

"""compute waiting time and transfered data size for every req in queue B"""
totalTSizeB   = 0
totalWTimeB   = 0
totalWtSavedB = 0
totalPSizeB = 0
reqWtSavedB	  = []
uReqRecorderB = []

for r in rQueueB:
	if r.left<=0:
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

	tmp = rQueueA[i].wt-r.wt
	reqWtSavedB.append(tmp)
	#totalWtSavedB += tmp

totalWtSavedB = totalWTimeA-totalWTimeB
totalPSizeB = min(totalSize,int(TL*value(pS.prob.objective)))

print "queue B (%d req) simulation finished." % len(rQueueB)
print "unfinished req in queue B  : %d" % len(uReqRecorderB)
print "total finished data size   : [%d KB], percent: [%%%.1f],increase: [%%%.1f]" % (totalTSizeB,totalTSizeB*100.0/totalSize,(totalTSizeB-totalTSizeA)*100.0/totalSize)
print "total waiting time saved   : [%d s], percent: [%%%.1f]" % (totalWtSavedB,totalWtSavedB*100.0/totalWTimeA)
print "total prefetching data size: [%d KB], percent: [%%%.1f]" % (totalPSizeB,totalPSizeB*100.0/totalSize)
print "\n"

"""---------------
debug information

for i,r in enumerate(rQueueB):
	print "r%3d, ti:%3d, Ti:%3d, wt_saved:[%%%5.1f], si_incr:[%%%.1f]" %\
	(i,r.at,r.ft,(rQueueA[i].wt-r.wt)*100.0/rQueueA[i].wt,(r.tsize-rQueueA[i].tsize)*100.0/r.size)
pause()
---------------"""

#evaluation
"""-----------------------------------------
evaluation

hit+false = N	
hit+miss = arrived
hit+false+miss = total

recall = hit/arrived = hit/(hit+miss)
precise = hit/N = hit/(hit+false) = (N-f)/N

hit:miss  = recall :(1-recall) ,recall>0
hit:false = precise:(1-precise),precise>0
-----------------------------------------"""
recall = 0.8		# hit:miss  = recall :(1-recall) ,recall>0
precise = 0.8		# hit:false = precise:(1-precise),precise>0

if recall==0.0:
	print "recall must be positive."
	exit()
else:
	hitCount   = int(precise*N)
	falseCount = N-hitCount
	missCount  = int(((1.0-recall)/recall)*hitCount)

rQueueC = []
rQueueM = []
rQueueD = []

"""miss requests follow a uniform random distribution"""
mDataGen = ReqDataGenerator()
mDataGen.genReqArrivalTime(missCount,T,dis="uniform")
mDataGen.genReqSize(missCount,dis="uniform")

for i in xrange(missCount):
	rQueueM.append(Request(TN))
	rQueueM[i].at = mDataGen.arrivalTime[i]/TL
	rQueueM[i].size = mDataGen.size[i]
	rQueueM[i].left = rQueueM[i].size
	rQueueM[i].flag = "miss"

"""queue C get parameters from queue B"""
for i in xrange(N):
	rQueueC.append(Request(TN))
	rQueueD.append(Request(TN))
	rQueueC[i].at   = rQueueB[i].at
	rQueueC[i].bdt  = rQueueB[i].ft
	rQueueC[i].size = rQueueB[i].size
	rQueueC[i].left = rQueueC[i].size
	rQueueC[i].idx  = i

	for t in xrange(TN):
		rQueueC[i].b[t] = rQueueB[i].b[t]

"""add false flag on random request"""
for i in sample(range(N),falseCount):
	rQueueC[i].flag = "false"

"""mix and sort queue C and queue M to get a new queue"""
rQueueC.extend(rQueueM)
rQueueC = sorted(rQueueC,key=attrgetter('at'))

rQueueD = deepcopy(rQueueC)

print "recall: [%2.1f], precise: [%2.1f]" % (recall,precise)
print "N: [%d], hit: [%d], miss: [%d], false: [%d], hit+miss: [%d]\n" \
	% (N,hitCount,missCount,falseCount,hitCount+missCount)

"""---------------
debug information

for i,r in enumerate(rQueueC):
	print "r%3d, ti:%3d, flag:%5s, Si:%5d" % (i,r.at,r.flag,r.size)
pause()
---------------"""

"""--------------------------------------------
simulate the process in queue D
step1.find active process
step2.simulate data transfer in current second
step3.get finished task info
--------------------------------------------"""
dReqRecorder  = []				#active req recorder
uReqRecorderD = []				#unfinished req in queue d

for t in xrange(TN):
	for r in rQueueD:
		if r.at<=t and r.left>0 and (r in dReqRecorder)==False:
			dReqRecorder.append(r)
		else:
			pass

	for r in dReqRecorder:
		if len(dReqRecorder)==0:
			break
		else:
			r.left -= (B/len(dReqRecorder))*TL

	for r in dReqRecorder[::-1]:
		if r.left <= 0:
			r.ft = t
			dReqRecorder.pop(dReqRecorder.index(r))
		else:
			pass

"""compute waiting time and transfered data size for every req in queue D"""
for r in rQueueD:
	if r.left <= 0:
		r.wt = r.ft-r.at+1
		r.tsize = r.size
		r.left = 0
	else:
		r.ft = TN-1
		r.wt = r.ft-r.at+1
		r.tsize = r.size-r.left
		uReqRecorderD.append(r)

totalSizeD  = 0
totalTSizeD = 0
totalWTimeD = 0

for r in rQueueD:
	totalSizeD  += r.size
	totalTSizeD += r.tsize
	totalWTimeD += r.wt

print "queue D (%d req) simulation finished." % len(rQueueD)
print "unfinished req in queue D: %d" % len(uReqRecorderD)
print "total request  data size: [%d KB]" % totalSizeD
print "total finished data size: [%d KB], percent: %%%.1f" % (totalTSizeD,totalTSizeD*100.0/totalSizeD)
print "total waiting time: [%d s]\n" % totalWTimeD

"""---------------
debug information

for i,r in enumerate(rQueueD):
	print "r%3d, ti:%3d, Ti:%3d, wt:%3d, Si:%5d, si:%5d" % (i,r.at,r.ft,r.wt,r.size,r.tsize)
pause()
---------------"""

"""------------------------------------------------------------
simulate the process in queue C
step1.find prefetch task,miss task and normal task in each slot
step2.pQueue --> nQueue(arrival time), nQueue --> mQueue(end time)
step3.simulate data transfer in current slot
step4.get finished task info
-------------------------------------------------------------"""
mReqRecorder  = []
pReqRecorder  = []
nReqRecorder  = []
sReqRecorder  = []
uReqRecorderC = []
totalPSizeC    = 0

for t in xrange(TN):
	for r in rQueueC:
		if r.left>0 \
		and (r in mReqRecorder) == False \
		and (r in pReqRecorder) == False \
		and (r in nReqRecorder) == False: 
			if   r.flag=="miss" and r.at<=t :
				mReqRecorder.append(r)
			elif r.flag!="miss" and r.at>t  :
				pReqRecorder.append(r)
			elif r.flag!="miss" and r.at<=t :
				nReqRecorder.append(r)
			else:
				pass
		else:
			pass

	for r in pReqRecorder[::-1]:
		if r.at<=t:
			nReqRecorder.append(pReqRecorder.pop(pReqRecorder.index(r)))
			continue
		else:
			pass

		if len(mReqRecorder)==0:
			r.left -= r.b[t]*TL
			totalPSizeC += r.b[t]*TL
		else:
			pass

	for r in nReqRecorder[::-1]:
		if r.bdt<=t:
			mReqRecorder.append(nReqRecorder.pop(nReqRecorder.index(r)))
			continue
		else:
			pass

		if len(mReqRecorder)==0:
			r.left -= r.b[t]*TL
		else:
			r.left -= (B/(len(mReqRecorder)+len(nReqRecorder)))*TL

	for r in mReqRecorder:
		r.left -= (B/(len(mReqRecorder)+len(nReqRecorder)))*TL

	for r in rQueueC:
		if r.left<=0 and r.ft == OT:
			if r.at>t:
				r.ft = r.at-1
			else:
				r.ft = t

			if   r in pReqRecorder:
				pReqRecorder.pop(pReqRecorder.index(r))
			elif r in nReqRecorder:
				nReqRecorder.pop(nReqRecorder.index(r))
			elif r in mReqRecorder:
				mReqRecorder.pop(mReqRecorder.index(r))
			else:
				pass
		else:
			pass	

"""compute waiting time and transfered data size for every req in queue C"""
for r in rQueueC:
	if r.left<=0:
		r.wt = r.ft-r.at+1
		r.tsize = r.size
		r.left = 0	
	else:
		r.ft = TN-1
		r.wt = r.ft-r.at+1
		r.tsize = r.size - r.left
		uReqRecorderC.append(r)

"""-------------------------------------------------------------------
C to D : schedule effect ,  count with miss
-------------------------------------------------------------------"""
totalTSizeC   = 0
totalWTimeC   = 0
totalWtSavedC = 0
reqWtSavedC   = []

fReqWtSavedC  = 0
uReqRecorderC = []

for i,r in enumerate(rQueueC):
	totalTSizeC += r.tsize
	totalWTimeC += r.wt

	tmp = rQueueD[i].wt - r.wt
	reqWtSavedC.append(tmp)

	if r.flag == "false":
		fReqWtSavedC += tmp

totalWtSavedC = totalWTimeD-totalWTimeC
totalPSizeC = min(totalPSizeC,totalSizeD)

print "queue C (%d req) simulation finished." % len(rQueueC)
print "unfinished req in queue C  : %d" % len(uReqRecorderC)
print "total finished data size   : [%d KB], percent: [%%%.1f],increase: [%%%.1f]" % (totalTSizeC,totalTSizeC*100.0/totalSizeD,(totalTSizeC-totalTSizeD)*100.0/totalSizeD)
print "total waiting time saved   : [%d s], percent: [%%%.1f]" % (totalWtSavedC,totalWtSavedC*100.0/totalWTimeD)
print "total prefetching data size: [%d KB], percent: [%%%.1f]" % (totalPSizeC,totalPSizeC*100.0/totalSizeD)
print "false  req waiting time saved: [%d s], percent: [%%%.1f]" % (fReqWtSavedC,fReqWtSavedC*100.0/totalWTimeD)
print "actual req waiting time saved: [%d s], percent: [%%%.1f]" % (totalWtSavedC-fReqWtSavedC,(totalWtSavedC-fReqWtSavedC)*100.0/totalWTimeD)
print "\n"

"""---------------
debug information

for i,r in enumerate(rQueueC):
	print "r%3d, ti:%3d, Ti:%3d, flag:%5s, wt_saved:[%%%5.1f], si_incr:[%%%.1f]" %\
	(i,r.at,r.ft,r.flag,(rQueueD[i].wt-r.wt)*100.0/rQueueD[i].wt,(r.tsize-rQueueD[i].tsize)*100.0/r.size)
pause()
---------------"""