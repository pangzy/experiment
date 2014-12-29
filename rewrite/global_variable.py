#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""global variables definition"""
TL 	 = TIMESLOT_LENGTH 	= 10         	# second
TN 	 = TIMESLOT_NUMBER 	= 360			# 
T    = TIME 			= TN*TL         # TN*TL = total time in time zone
F    = REQUEST_FREQUENCY= 20			# request frequency , seconds/req, F=T/N
N    = REQUEST_NUMBER	= (T/F)			# request number in queue_a
B 	 = BANDWIDTH		= 512			# KB/s
MAXS = MAX_SINGLE_SIZE	= 1*1024		# KB
MINS = MIN_SINGLE_SIZE	= 1 			# KB

DATAFILEPATH = 'D:\Experiment\prefetching-simulation\data2.xls'
RESULTFILEPATH = 'D:\Experiment\prefetching-simulation\\result.xls'

OT	   = TIME_OUT_OF_RANGE = -1 		# time out of [0,T]	

#S 	 = STORAGE			= 200*1024*1024 			# 200GB, not in use

