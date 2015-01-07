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

a = slc.Queue()
b = slc.Queue()

if args["source"] == "g":
    a.gen_queue(args["dis"])
    b.inh_queue(a.queue)
elif args["source"] == "l":
    a.load_queue(pos)
    b.inh_queue(a.queue)
elif args["source"] == "r":
    pass
else:
    print "data source argument wrong."
    exit()

sim = slc.Simulator()
sim.process(a.queue)
sim.solve(a.queue,b.queue)
sim.process(b.queue, with_schedule=True)

c = slc.Queue()
d = slc.Queue()

if args["source"] == "r" :
    pass
else :
    c.inh_queue(b.queue)
    c.mix_queue(recall, precise)
    d.inh_queue(c.queue)

sim.process(d.queue)
sim.process(c.queue, with_schedule=True)

print "finished."






