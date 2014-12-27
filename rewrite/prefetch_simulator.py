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
		rQueueA.append(Request(T))
		rQueueB.append(Request(T))

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
		rQueueA.append(Request(T))
		rQueueB.append(Request(T))

		rQueueA[i].at   = dLoader.arrivalTime[i]/TL 	# ti --> timeslot_index
		rQueueA[i].size = dLoader.size[i]
		rQueueA[i].left = rQueueA[i].size

		rQueueB[i].at   = rQueueA[i].at
		rQueueB[i].size = rQueueA[i].size
		rQueueB[i].left = rQueueA[i].left

else:
	print 'wrong argument!'
	exit()

print 'data ok.\n'

"""--------------------------------------------
simulate the process in queue_a
step1.find active process
step2.simulate data transfer in current second
step3.get finished task info
--------------------------------------------"""
aReqRecorder = []				#active req recorder

for t in xrange(T):
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
			if r.left <= 0:

	for r in rQueueA:

