#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""import global module"""
import copy
import random
from operator import itemgetter, attrgetter 
from glv import *
from class_def import *


"""
queue_a is the normal predicted request queue without prefetch schedule
queue_b is the queue after prefetch schedule
"""
rQueueA = range(N)
rQueueB = range(N)

for i in xrange(N):
	rQueueA[i] = rQueueB[i] = Request(T)

"""generate or load base data about queue_a"""
dGen = DataGenerator(N,T)
dGen.genReqArrivalTime(N,T)
dGen.sortReqArrivalTime()
dGen.genReqSize(N,T)

for i in xrange(N):
	rQueueA[i].at = dGen.reqArrvalTime[i]
	rQueueA[i].size = dGen.reqSize[i]
	rQueueA[i].left = rQueueA[i].size
"""

'''load queue_a data'''
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

"""queue_b get arrival time,size,left_size from queue_a"""
rQueueB = copy.deepcopy(rQueueA)

print 'data genaration finished\n'

"""simulate the process in queue_a"""
reqActive = 0
bActive = B
totalReqSize = 0
totalWaitingTimeA = 0
reqUnfinishedA = []

"""
step1.find active process
step2.simulate data transfer in current second
step3.get finished task info
"""
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

"""compute waiting time and transfered data size for every req in queue_a"""
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

"""simulate the process in queue_b"""
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
#recall = 0.3
#precise = 0.2
#
#falseCount = int((1.0-precise)*N)
#hitCount = N-falseCount
#missCount = int(((1.0-recall)/recall)*hitCount)
#plusT = T
#deltaT = 5
#atDisturbancePercent = 0.2
#atDisturbanceCount = int(N*atDisturbancePercent)

recall = 0
precise = 0

falseCount = 0
hitCount = N-falseCount
missCount = 0
plusT = T
deltaT = 5
atDisturbancePercent = 0
atDisturbanceCount = 0

"""evaluation queues"""
rQueueC = range(N)
rQueueM = range(missCount)
rQueueD = range(N)			#queue_a'

for i in xrange(len(rQueueC)):
	rQueueC[i] = Request(T)

for i in xrange(len(rQueueM)):
	rQueueM[i] = Request(T)

for i in xrange(len(rQueueD)):
	rQueueD[i] = Request(T)

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

print '\n'
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

#for i in xrange(len(rQueueC)):
#	print 'c%d : %d %d %d %d %d' % (i,rQueueC[i].at,rQueueC[i].size,rQueueC[i].left,rQueueC[i].miss,rQueueC[i].false)
#print '\n'
"""schedule queue_c"""
mReqRecorder = []
pReqRecorder = []
nReqRecorder = []
sReqRecorder = []
reqUnfinishedC = []
for j in xrange(T+1):
	bAvailable = B
	for r in rQueueC:
		if r.left>0 \
		and (r in mReqRecorder) == False \
		and (r in pReqRecorder) == False \
		and (r in nReqRecorder) == False: 				#unfinished task
			if r.miss==1 and r.at<=j:					#if it's a miss			
				mReqRecorder.append(r)
			elif r.miss!=1 and r.at>j and r.bb[j]>0:	#if it's a prefetch	
				pReqRecorder.append(r)
			elif r.miss!=1 and r.at<=j and r.bb[j]>0:	#if it's a normal request
				nReqRecorder.append(r)
			else:
				pass
		elif r.sindex != -1:
			r.ft = r.at-1
		else:
			pass

	'''if there is a miss,prefetch suspend,
	   and the total suspended part become a new miss at the end of this req '''		
	for r in pReqRecorder:	
		if r.at<=j:
			nReqRecorder.append(pReqRecorder.pop(pReqRecorder.index(r)))
		else:
			pass

		if len(mReqRecorder)!=0:
			if r.bb[j]>0:
				r.st = j
			else:
				pass
		else:
			r.left -= r.bb[j]*TL
			if r.st!=-1:
				r.se = j
				for t in xrange(r.st,r.se):
					r.sizesus += r.bb[t]*TL
				newReq = Request(T)
				newReq.size = r.sizesus
				newReq.sindex = rQueueC.index(r)
				newReq.miss = 1
				sReqRecorder.append(newReq)

		if r.left<=0: 							#prefetch finished before req arrive
			r.ft = r.at-1
			pReqRecorder.pop(pReqRecorder.index(r))

	'''normal request proceed as usual'''
	for r in nReqRecorder:						
		bAvailable -= r.bb[j]
		r.left -= r.bb[j]*TL
		if r.left<=0:
			r.ft = j
			nReqRecorder.pop(nReqRecorder.index(r))
		else:
			pass

	'''miss request share remaining bandwidth'''
	for r in mReqRecorder:						
		r.left -= (bAvailable/len(mReqRecorder))*TL
		if r.left<=0:
			r.ft = j
			mReqRecorder.pop(mReqRecorder.index(r))
		else:
			pass

	'''process the suspend part'''
	for r in sReqRecorder:
		if rQueueC[r.sindex].ft != -1:
			rQueueC[r.sindex].left += r.sizesus
			rQueueC.append(r)
		else:
			pass

for r in rQueueC:
	i = rQueueC.index(r)
	if r.left > 0:
		r.ft = T
		r.wt = T-r.at+1
		reqUnfinishedC.append(i)
	else:
		r.wt = r.ft-r.at+1

for r in rQueueC:
	print 'c%d : %d %d %d %d %d' % (rQueueC.index(r),r.at,r.size,r.ft,r.wt,r.miss)