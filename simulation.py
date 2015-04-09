#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import *
# from math import ceil, floor
from copy import deepcopy
from generator import generate

arg = load_arguments("arguments.conf")
start_time = arg["start_time"]
end_time = start_time + arg["time_length"]
generate(arg["time_length"], 5)
q_file = ("a.txt", "b.txt", "c.txt")
q_list = load_queue(q_file)
qa = q_list[0]
qb = q_list[1]
qc = q_list[2]
qa2 = deepcopy(qa)
qb2 = deepcopy(qb)
qc2 = deepcopy(qc)

start_hour = start_time / 3600
end_hour = end_time / 3600 + 1

for r in qa:
    if r.flag == "miss":
        print "miss req in queue A."
        exit()

print "total request in queue A : %d" % (len(qa))
print "req freq : %f (sec/req)" % (arg["time_length"]/float(len(qa)))
print "simulate queue A without schedule."
simulate3(arg=arg, queue=qa, scheduled=False)
slot_end = get_slot(qa)
simulate3(arg=arg, queue=qa2, scheduled=False)

print "schedule queue A."
s_list = schedule(arg=arg, queue=qa, slot_end=slot_end)
s_list2 = schedule2(qa2)
print len(s_list)
print len(s_list2)

# print "simulate queue A with schedule."
# simulate(s_list=s_list, arg=arg, queue=qa, scheduled=True)
# simulate2(s_list=s_list, arg=arg, queue=qa2, scheduled=True)
# res_a = stats(queue=qa)
# res_a2 = stats(queue=qa2)
# output(arg=arg, res=res_a, st=start_time, et=end_time, tag="queue A")
# output(arg=arg, res=res_a2, st=start_time, et=end_time, tag="queue A2")

print "total request in queue B : %d" % (len(qb))
print "req freq : %f (sec/req)" % (arg["time_length"]/float(len(qb)))
print "simulate queue B."
simulate3(arg=arg, queue=qb, scheduled=False)
simulate3(arg=arg, queue=qb2, scheduled=False)

print "get schedule data from queue A."
# transfer(s_list, qc, qa, arg)
# transfer(s_list2, qc2, qa2, arg)
wf1 = open("list.txt", "w")
wf2 = open("list2.txt", "w")
wf1.write(str(s_list))
wf2.write(str(s_list2))
wf1.close()
wf2.close()

print "simulate queue C with schedule."
simulate3(s_list=s_list, arg=arg, queue=qc, scheduled=True)
simulate3(s_list=s_list2, arg=arg, queue=qc2, scheduled=True)

transfer(qb, qc)
transfer(qb2, qc2)

print "stats."

res_a = stats(queue=qa)
res_b = stats(queue=qb)
res_c = stats(queue=qc)
res_a2 = stats(queue=qa2)
res_b2 = stats(queue=qb2)
res_c2 = stats(queue=qc2)

print "output."

output(arg=arg, res=res_b, st=start_time, et=end_time, tag="queue B")
output(arg=arg, res=res_b2, st=start_time, et=end_time, tag="queue B2")
# output(arg=arg, res=res_c, st=start_time, et=end_time, tag="queue C")
# output(arg=arg, res=res_c2, st=start_time, et=end_time, tag="queue C2")

# exit()
print "write."
wrt(arg=arg, res=res_a, q=qa, file="a.result")
wrt(arg=arg, res=res_b, q=qb, file="b.result")
wrt(arg=arg, res=res_c, q=qc, file="c.result")
wrt(arg=arg, res=res_a2, q=qa2, file="a2.result")
wrt(arg=arg, res=res_b2, q=qb2, file="b2.result")
wrt(arg=arg, res=res_c2, q=qc2, file="c2.result")

if __name__ == '__main__':
    pass
