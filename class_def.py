#!/usr/bin/env python
# -*- coding: utf-8 -*-

#class definations

import random
import math
from pulp import *
from glv import *
from xlrd import *

def pause():
	if raw_input("press any key to continue:"):
		pass

class Request(object):
	"""common base class for all request"""

	def __init__(self,T):
		self.at 	= 0				#arrival time
		self.ft 	= -1			#finish time
		self.wt 	= 0				#waiting time
		self.size 	= 0				#data size
		self.sizegot= 0				#data size in T
		self.state 	= 0				#process state
		self.left 	= 0				#left size at timeslot j
		self.miss	= 0
		self.pstate	= range(T+1)	#prefetch state
		self.ab 	= range(T+1)	#bandwidth for ri at timeslot j in queue A
		self.bb 	= range(T+1)	#bandwidth for ri at timeslot j in queue B
		self.cb 	= range(T+1)	#bandwidth for ri at timeslot j in queue C

		for j in xrange(T+1):
			self.state 		= 0
			self.pstate[j]	= 0	
			self.ab[j] 		= 0
			self.bb[j] 		= 0
			self.cb[j] 		= 0	

'''
class RQueue(object):
	
	def __init__(self,N,T):
		self.length = N
		self.req 	= range(N)

		for i in xrange(N):
			self.req[i] = Request(N,T)
'''

class DataGenerator(object):
	"""docstring for DataGenerator"""
	def __init__(self,N,T):
		self.reqArrvalTime = range(N)
		self.reqSize = range(N)
	
	def genReqArrivalTime(self,N,T):
		for i in xrange(N):
			self.reqArrvalTime[i] = random.randint(0,T)

	def genReqSize(self,N,T):	
		for i in xrange(N):
			self.reqSize[i] = random.randint(MINS,MAXS)

	def sortReqArrivalTime(self):
		self.reqArrvalTime.sort()

class DataLoader(object):
	"""docstring for DataLoader"""
	def __init__(self):		
		self.reqArrvalTime = []
		self.reqSize = []
		self.reqNum = 0
		self.timeSlotLength = 1
		self.timeSlotNum = 0

	def loadData(self):
		xlsFile 	= open_workbook(DATAFILEPATH)
		table		= xlsFile.sheet_by_index(1)
		timeData 	= table.col_values(1)
		sizeData	= table.col_values(2)
#		startRow 	= 188
#		endRow		= 266
		startRow 	= 514
		endRow		= 636
		self.reqNum	= endRow-startRow+1
		startTime 	= int(timeData[startRow]*24)
		endTime 	= int(timeData[endRow]*24)+1
		self.timeSlotNum = (endTime-startTime)*3600/self.timeSlotLength

		for i in range(startRow,endRow+1):
			t = int(timeData[i]*24*60*60) - startTime*60*60
			self.reqArrvalTime.append(t)
			s = int(math.ceil(sizeData[i]/1024))
			self.reqSize.append(s)

class LPSolver(object):
	"""docstring for LPSolver"""
	def __init__(self):
		pass

	def defProblem(self,rQueueB,rQueueA,N,T):
		rIdx = range(N)
		tIdx = range(T+1)
		ti 	 = range(N)
		si 	 = range(N)
		Ti   = range(N)
 		
		for i in xrange(N):
			rIdx[i] = str(i)
			ti[i]	= rQueueB[i].at
			si[i]	= rQueueA[i].sizegot
			Ti[i] 	= rQueueA[i].ft
		
		for j in xrange(T+1):
			tIdx[j] = str(j)

		self.varb = LpVariable.dicts('b',(rIdx,tIdx),0,B,LpInteger)
		self.prob = LpProblem('Prefetching Schedule',LpMaximize)
		
		#objective function : sigma bij
		"""
		for i in rIdx:
			rInt = int(i)
			for j in range(ti[rInt]):
				t = str(j)
				self.prob += self.varb[i][t]
		"""

		self.prob += lpSum([self.varb[i][t] for i in rIdx for t in tIdx if int(t)<ti[int(i)]])
		
		#constraints: sigma bi <= B
		for t in tIdx:
		 	self.prob += lpSum([self.varb[i][t] for i in rIdx])<=B

		#constraints: from 0 to Ti,sigma bij <= sizegot
		for i in rIdx:	
			self.prob += lpSum(self.varb[i][t] for t in tIdx if int(t)<=Ti[int(i)]) == si[int(i)]/TL

	def solveProblem(self):
		self.probStatus = self.prob.solve()

		print LpStatus[self.probStatus]

	def exportData(self,rQueueB,N,T):
		for i in xrange(N):
			for t in xrange(T+1):
				rQueueB[i].bb[t] = int(value(self.varb[str(i)][str(t)]))			

