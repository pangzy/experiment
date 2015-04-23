#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import os


def test():
    recall_range = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)
    precision_range = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)
    activity = ("disuse", "slight", "normal", "heavy")

    # home test No.1
    '''
    for i in xrange(2, 4):      # activity
        for t in xrange(1, 6):      # time interval
            for j in xrange(1, 31):      # user number
                wf = open("result.dat", "a")
                wf.writelines("\n")
                wf.close()
                for rc in recall_range:
                    cf = ConfigParser()
                    cf.read("arguments.conf")
                    if t == 5:
                        cf.set("arguments", "time_interval", "0~900")
                    else:
                        cf.set("arguments", "time_interval", "0~"+str(3600*t))
                    cf.set("arguments", "activity", activity[i])
                    cf.set("arguments", "user_number", j)
                    cf.set("prediction", "precision", "1.0")
                    cf.set("prediction", "recall", str(rc))
                    cf.write(open("arguments.conf", "w"))
                    for k in xrange(5):
                        os.system("simulation.py")

                wf = open("result.dat", "a")
                wf.writelines("\n")
                wf.close()
                for pcs in precision_range:
                    cf = ConfigParser()
                    cf.read("arguments.conf")
                    if t == 5:
                        cf.set("arguments", "time_interval", "0~900")
                    else:
                        cf.set("arguments", "time_interval", "0~"+str(3600*t))
                    cf.set("arguments", "activity", activity[i])
                    cf.set("arguments", "user_number", j)
                    cf.set("prediction", "recall", "1.0")
                    cf.set("prediction", "precision", str(pcs))
                    cf.write(open("arguments.conf", "w"))
                    for k in xrange(5):
                        os.system("simulation.py")
    '''

    # test no 2
    for j in xrange(1, 30):      # user number
            # wf = open("result.dat", "a")
            # wf.writelines("\n")
            # wf.close()
            #for rc in recall_range:
            cf = ConfigParser()
            cf.read("arguments.conf")
            cf.set("arguments", "time_interval", "0~"+str(j*60))
            cf.set("arguments", "activity", "normal")
            cf.set("arguments", "user_number", j)
            cf.set("prediction", "precision", "1.0")
            cf.set("prediction", "recall", "1.0")
            cf.write(open("arguments.conf", "w"))
            os.system("simulation.py")


if __name__ == '__main__':
    test()