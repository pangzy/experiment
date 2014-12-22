#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import random
from operator import itemgetter, attrgetter 
from glv import *
from class_def import *


'''generate request queue A data'''
rQueueA = range(N)
rQueueB = range(N)

for i in xrange(N):
	rQueueA[i] = rQueueB[i] = Request(T)

dGen = DataGenerator(N,T)
dGen.genReqArrivalTime(N,T)
dGen.sortReqArrivalTime()
dGen.genReqSize(N,T)

for i in xrange(N):
	rQueueA[i].at = dGen.reqArrvalTime[i]
	rQueueA[i].size = dGen.reqSize[i]
	rQueueA[i].left = rQueueA[i].size
"""

'''load request queue A data'''
dLoader = DataLoader()
dLoader.loadData()
TL = dLoader.timeSlotLength
T  = dLoader.timeSlotNum
N  = dLoader.reqNum

rQueueA = range(N)
rQueueB = range(N)

for i in xrange(N):
	rQueueA[i] = rQueueB[i] = Request(T)

for i in xrange(N):
	rQueueA[i].at = dLoader.reqArrvalTime[i]
	rQueueA[i].size = dLoader.reqSize[i]
	rQueueA[i].left = rQueueA[i].size
"""

rQueueB = copy.deepcopy(rQueueA)

print 'data genaration finished\n'

#compute origin queue A parameter
reqActive = 0
bActive = B
totalReqSize = 0
totalWaitingTimeA = 0
reqUnfinishedA = []

for j in xrange(T+1):
	for i in xrange(N):
		if rQueueA[i].at<=j and rQueueA[i].left>0 and rQueueA[i].state==0:
			rQueueA[i].state = 1
			reqActive += 1			
		else :
			pass

	for i in xrange(N):
		if reqActive != 0:
			bActive = B/reqActive
			rQueueA[i].left -= 	bActive*TL*rQueueA[i].state			
		else:
			pass

	for i in xrange(N):
		if rQueueA[i].left <= 0 and rQueueA[i].state==1:
			rQueueA[i].state = 0
			rQueueA[i].ft = j
			reqActive -= 1

for i in xrange(N):
	if rQueueA[i].ft != -1 :
		rQueueA[i].wt = rQueueA[i].ft-rQueueA[i].at+1
		rQueueA[i].sizegot = rQueueA[i].size
	else:	 
		reqUnfinishedA.append(i)
		rQueueA[i].ft = T
		rQueueA[i].wt = T-rQueueA[i].at+1
		rQueueA[i].sizegot = rQueueA[i].size - rQueueA[i].left

for i in xrange(N):
	totalReqSize += rQueueA[i].size
	totalWaitingTimeA += rQueueA[i].wt

print 'queue_a compute finished'
print 'total request data size : %d' % totalReqSize
print 'total waiting time in queue a : %d' % totalWaitingTimeA
print 'unfinished req in queue a : %d\n' % len(reqUnfinishedA)
#pause()
#print 'ri : ti si ft wt'
#for i in xrange(N):
#	print 'r%d : %d %d %d %d' % (i,rQueueA[i].at,rQueueA[i].size,rQueueA[i].ft,rQueueA[i].wt)
#pause()

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
		if rQueueB[i].left > 0:
			rQueueB[i].left -= rQueueB[i].bb[j]*TL
		elif rQueueB[i].ft == -1 and rQueueB[i].at >= j:
			rQueueB[i].ft = rQueueB[i].at-1
		elif rQueueB[i].ft == -1:
			rQueueB[i].ft = j-1
		else:
			pass

for i in xrange(N):
	if rQueueB[i].left > 0:
		rQueueB[i].ft = T
		rQueueB[i].wt = T-rQueueB[i].at+1
		reqUnfinishedB.append(i)
	else:
		rQueueB[i].wt = rQueueB[i].ft-rQueueB[i].at+1
		wtSaved += (rQueueA[i].wt-rQueueB[i].wt)


for i in xrange(N):
	print 'r%d : %d %d %d %d' % (i,rQueueB[i].at,rQueueB[i].size,rQueueB[i].ft,rQueueB[i].wt)

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
"""evaluation variables"""
recall = 0.3
precise = 0.2

falseCount = int((1.0-precise)*N)
hitCount = N-falseCount
missCount = int(((1.0-recall)/recall)*hitCount)
plusT = T
deltaT = 5
atDisturbancePercent = 0.2
atDisturbanceCount = int(N*atDisturbancePercent)

"""evaluation queues"""
rQueueC = range(N)
rQueueM = range(missCount)

for i in xrange(len(rQueueC)):
	rQueueC[i] = Request(T+plusT)

for i in xrange(len(rQueueM)):
	rQueueM[i] = Request(T+plusT)

"""miss and false data genaratation
   generate missed request queue"""
missDataGen = DataGenerator(missCount,T)
missDataGen.genReqArrivalTime(missCount,T)
missDataGen.sortReqArrivalTime()
missDataGen.genReqSize(missCount,T)

for i in xrange(len(rQueueM)):
	rQueueM[i].at = missDataGen.reqArrvalTime[i]
	rQueueM[i].size = missDataGen.reqSize[i]
	rQueueM[i].left = rQueueM[i].size
	rQueueM[i].miss = 1

"""add false flag on stochastic request"""
for i in random.sample(range(N),falseCount):
	rQueueC[i].false = 1

#for i in xrange(missCount):
#	print 'm%d : %d %d %d' % (i,rQueueM[i].at,rQueueM[i].size,rQueueM[i].left)

"""queue_c get parameters from queue_b"""
for i in xrange(len(rQueueC)):
	rQueueC[i].at = rQueueB[i].at
	rQueueC[i].size = rQueueB[i].size
	rQueueC[i].left = rQueueC[i].size

	if i in reqUnfinishedB:
		rQueueC[i].sizegot = rQueueC[i].size-rQueueC[i].left
	else:
		rQueueC[i].sizegot = rQueueC[i].size

	for j in xrange(T+1):
		rQueueC[i].bb[j] = rQueueB[i].bb[j]

"""add deltaT Disturbance on stochastic request"""
for i in random.sample(range(N),atDisturbanceCount):
	print "before: r%d : %d" % (i,rQueueC[i].at)

	rQueueC[i].at += random.randint((-1)*deltaT,deltaT)
	if rQueueC[i].at < 0:
		rQueueC[i].at = 0
	elif rQueueC[i].at > T:
		rQueueC[i].at = T
	else:
		pass

	print "after: r%d : %d" % (i,rQueueC[i].at)


"""mix queue_c and miss data,then sort the new queue"""
rQueueC.extend(rQueueM)
rQueueC = sorted(rQueueC,key=attrgetter('at'))	

print '\n'
for i in xrange(len(rQueueC)):
	print 'c%d : %d %d %d %d %d' % (i,rQueueC[i].at,rQueueC[i].size,rQueueC[i].left,rQueueC[i].miss,rQueueC[i].false)

"""schedule queue_c"""
#for j in xrange(T+1):

