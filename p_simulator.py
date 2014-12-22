#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from glv import *
from class_def import *


'''generate request queue A data'''
rQueueA = RQueue(N,T)
rQueueB = RQueue(N,T)
dGen = DataGenerator(N,T)
dGen.genReqArrivalTime(N,T)
dGen.sortReqArrivalTime()
dGen.genReqSize(N,T)

for i in xrange(N):
	rQueueA.req[i].at = dGen.reqArrvalTime[i]
	rQueueA.req[i].size = dGen.reqSize[i]
	rQueueA.req[i].left = rQueueA.req[i].size
"""

'''load request queue A data'''
dLoader = DataLoader()
dLoader.loadData()
TL = dLoader.timeSlotLength
T  = dLoader.timeSlotNum
N  = dLoader.reqNum

rQueueA = RQueue(N,T)
rQueueB = RQueue(N,T)

for i in xrange(N):
	rQueueA.req[i].at = dLoader.reqArrvalTime[i]
	rQueueA.req[i].size = dLoader.reqSize[i]
	rQueueA.req[i].left = rQueueA.req[i].size
"""
rQueueB.req = copy.deepcopy(rQueueA.req)

print 'data genaration finished\n'

#compute origin queue A parameter
reqActive = 0
bActive = B
totalReqSize = 0
totalWaitingTimeA = 0
reqUnfinishedA = []

for j in xrange(T+1):
	for i in xrange(N):
		if rQueueA.req[i].at<=j and rQueueA.req[i].left>0 and rQueueA.req[i].state==0:
			rQueueA.req[i].state = 1
			reqActive += 1			
		else :
			pass

	for i in xrange(N):
		if reqActive != 0:
			bActive = B/reqActive
			rQueueA.req[i].left -= 	bActive*TL*rQueueA.req[i].state			
		else:
			pass

	for i in xrange(N):
		if rQueueA.req[i].left <= 0 and rQueueA.req[i].state==1:
			rQueueA.req[i].state = 0
			rQueueA.req[i].ft = j
			reqActive -= 1

for i in xrange(N):
	if rQueueA.req[i].ft != -1 :
		rQueueA.req[i].wt = rQueueA.req[i].ft-rQueueA.req[i].at+1
		rQueueA.req[i].sizegot = rQueueA.req[i].size
	else:	 
		reqUnfinishedA.append(i)
		rQueueA.req[i].ft = T
		rQueueA.req[i].wt = T-rQueueA.req[i].at+1
		rQueueA.req[i].sizegot = rQueueA.req[i].size - rQueueA.req[i].left

for i in xrange(N):
	totalReqSize += rQueueA.req[i].size
	totalWaitingTimeA += rQueueA.req[i].wt

print 'queue_a compute finished'
print 'total request data size : %d' % totalReqSize
print 'total waiting time in queue a : %d' % totalWaitingTimeA
print 'unfinished req in queue a : %d\n' % len(reqUnfinishedA)
pause()
print 'ri : ti si ft wt'
for i in xrange(N):
	print 'r%d : %d %d %d %d' % (i,rQueueA.req[i].at,rQueueA.req[i].size,rQueueA.req[i].ft,rQueueA.req[i].wt)
pause()

"""
solve optimization problem,linear program
use PuLP & GPLK
"""
reqUnfinishedB = []
wtSaved = 0
totalWaitingTimeB = 0
pS = LPSolver()
pS.defProblem(rQueueB,rQueueA,N,T)
pS.solveProblem()
pS.exportData(rQueueB,N,T)

print 'problem solve finisded\n'

#scheduling queue B
for j in xrange(T+1):
	for i in xrange(N):
		if rQueueB.req[i].left > 0:
			rQueueB.req[i].left -= rQueueB.req[i].bb[j]*TL
		elif rQueueB.req[i].ft == -1 and rQueueB.req[i].at >= j:
			rQueueB.req[i].ft = rQueueB.req[i].at-1
		elif rQueueB.req[i].ft == -1:
			rQueueB.req[i].ft = j-1
		else:
			pass

for i in xrange(N):
	if rQueueB.req[i].left > 0:
		rQueueB.req[i].ft = T
		rQueueB.req[i].wt = T-rQueueB.req[i].at+1
		reqUnfinishedB.append(i)
	else:
		rQueueB.req[i].wt = rQueueB.req[i].ft-rQueueB.req[i].at+1
		wtSaved += (rQueueA.req[i].wt-rQueueB.req[i].wt)


for i in xrange(N):
	print 'r%d : %d %d %d %d' % (i,rQueueB.req[i].at,rQueueB.req[i].size,rQueueB.req[i].ft,rQueueB.req[i].wt)

print '\n'
print 'The optimization problem is solved :'+ LpStatus[pS.probStatus]
print 'unfinished req in queue_b : %d' % len(reqUnfinishedB)
print 'Total waiting time saved  : %d,percent : %%%d' % (wtSaved,int(wtSaved*100/totalWaitingTimeA))
print 'Total prefechting data size : %d,percent : %%%d' % (int(TL*value(pS.prob.objective)),int(TL*value(pS.prob.objective))*100/totalReqSize)

#evaluation
"""
	hit+false = N	
	hit+miss = arrived
	hit+false+miss = total

	recall = hit/arrived = hit/(hit+miss)
	precise = hit/N = hit/(hit+false) = (N-f)/N
"""
recall = 0.3
precise = 0.2

falseCount = int((1-precise)*N)
hitCount = N-falseCount
missCount = int(((1-recall)/recall)*recall)

deltaT = T

rQueueC = RQueue(N+missCount,T+deltaT)
rQueueM = RQueue(missCount,T)

missDataGen = DataGenerator(missCount,T)
missDataGen.genReqArrivalTime(missCount,T)
missDataGen.sortReqArrivalTime()
missDataGen.genReqSize(missCount,T)

print "miss req data generated."

for i in xrange(N):
	rQueueC.req[i].at = rQueueB.req[i].at
	rQueueC.req[i].size = rQueueB.req[i].size
	rQueueC.req[i].left = rQueueC.req[i].size

	if i in reqUnfinishedB:
		rQueueC.req[i].sizegot = rQueueC.req[i].size-rQueueC.req[i].left
	else:
		rQueueC.req[i].sizegot = rQueueC.req[i].size

	for j in xrange(T+1):
		rQueueC.req[i].bb[j] = rQueueB.req[i].bb[j]

for i in xrange(N,N+missCount):
	rQueueM.req[i].at = missDataGen.reqArrvalTime[i]
	rQueueM.req[i].size = missDataGen.reqSize[i]
	rQueueM.req[i].left = rQueueM.req[i].size

print "mixing data ..."

rQueueC.extend(rQueueM)
rQueueC = sorted(rQueueC,key=attrgetter(req.at))	
