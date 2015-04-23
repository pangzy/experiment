#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_avg():
    f = open("result.dat")
    lines = f.readlines()
    buf = []
    new_lines = ""

    for i, line in enumerate(lines):
        ls = line.split()
        t = ls[1].split(")")[0]
        un = ls[2].split("[")[1].split("]")[0]
        ac = ls[3].split("'")[1]
        rc = ls[4][1:4]
        pcs = ls[5][1:4]
        rls = ls[6]
        psp = ls[7]
        rac = ls[8]
        avgs = ls[9]
        avgi = ls[10]
        avgtf = ls[11]
        l = t+"\t"+un+"\t"+ac+"\t"+rc+"\t"+pcs+"\t"+rls+"\t"+psp+"\t"+rac+"\t"+avgs+"\t"+avgi+"\t"+avgtf+"\n"
        new_lines += l

        '''
        if line != "\n":
            buf.append(line)
            if len(buf) >= 5:
                line0 = buf[0]
                ls = line0.split()
                t = ls[1].split(")")[0]
                un = ls[2].split("[")[1].split("]")[0]
                ac = ls[3].split("'")[1]
                rc = ls[4][1:4]
                pcs = ls[5][1:4]
                prefix = "{0}\t{1}\t{2}\t{3}\t{4}\t".format(t, un, ac, rc, pcs)
                rls = sum([float(x.split()[6]) for x in buf])/len(buf)
                psp = sum([float(x.split()[7]) for x in buf])/len(buf)
                rac = sum([float(x.split()[8]) for x in buf])/len(buf)
                l = prefix+str(rls)+"\t"+str(psp)+"\t"+str(rac)+"\n"
                new_lines += l
                buf = []
        '''
    wf = open("test2.txt", "w")
    wf.writelines(new_lines)
    wf.close()


def user_change():
    f = open("result-1.dat")
    lines = f.readlines()

    lines.sort(key=lambda i: float(i.split()[3]))

    w = open("user_change.txt", "w")
    w.writelines(lines)
    w.close()

if __name__ == '__main__':
    get_avg()
    # user_change()