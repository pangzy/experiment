#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import
import slc
import glv

# ----------------------------------------------------
# args: 
#
#
# ----------------------------------------------------

glv.load_args()
args = glv.get_glv()

pos = {}
pos["sheet_index"] = args["sheet_index"]
pos["start_row"] = args["start_row"]
pos["end_row"] = args["end_row"]
pos["time_col"] = args["time_col"]
pos["size_col"] = args["size_col"]

recall = args["recall"]
precise = args["precise"]

queue_a = slc.Queue()
queue_b = slc.Queue()

if args["source"] == "g":
    queue_a.gen_queue(args["dis"])
    queue_b.inh_queue(queue_a.queue)
elif args["source"] == "l":
    queue_a.load_queue(pos)
    queue_b.inh_queue(queue_a.queue)
elif args["source"] == "r":
    pass
else:
    print "data source argument wrong."
    exit()

sim = slc.Simulator()
sim.process(queue_a.queue)
sim.solve(queue_a.queue,queue_b.queue)
sim.process(queue_b.queue, with_schedule=True)

queue_c = slc.Queue()
queue_d = slc.Queue()

if args["source"] == "r" :
    pass
else :
    queue_c.inh_queue(queue_b.queue)
    queue_c.mix_queue(recall, precise)
    queue_d.inh_queue(queue_c.queue)

sim.process(queue_d.queue)
sim.process(queue_c.queue, with_schedule=True)

print "finished."






