#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


def pause():
    if raw_input("press any key to continue:"):
        pass

list_dir = os.listdir(os.getcwd())

for line in list_dir:
    if os.path.isfile(line) and ".dat" in line:
        print "processing\t" + line
        # cmd1 = "filter_get.py" + " " + line
        # cmd2 = "filter_response.py" + " " + line
        # cmd3 = "match.py" + " " + line
        # os.system(cmd1)
        # print "finish get filter."
        # os.system(cmd2)
        # print "finish response filter."
        # os.system(cmd3)
        # print "finish match."
        cmd3 = "match_sup.py" + " " + line
        os.system(cmd3)
        print "finish match."

print "finish all."