#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import defaultdict
from time import strptime, mktime


def pause():
    if raw_input("press any key to continue:"):
        pass


def reassemble_from_date():
    list_dir = os.listdir(os.getcwd())
    date_list = []
    record_list = []

    for item in list_dir:
        if os.path.isfile(item) and ".dat" in item:
            f = open(item)
            lines = f.readlines()
            for line in lines:
                ls = line.split()
                date = ls[0]
                if date in date_list:
                    idx_rl = date_list.index(date)
                    record_list[idx_rl].append(line)
                else:
                    date_list.append(date)
                    record_list.append([line])

    for i, item in enumerate(record_list):
        date = date_list[i]
        file_wrt = date+".http"
        wf = open(file_wrt, "w")
        wf.writelines(item)
        wf.close()


def rename_user():
    list_dir = os.listdir(os.getcwd())
    alphabet = ("A", "B", "C", "D", "E", "F", "G",
                "H", "I", "J", "K", "L", "M", "N",
                "O", "P", "Q", "R", "S", "T",
                "U", "V", "W", "X", "Y", "Z",
                "a", "b", "c", "d", "e", "f", "g",
                "h", "i", "j", "k", "l", "m", "n",
                "o", "p", "q", "r", "s", "t",
                "u", "v", "w", "x", "y", "z")
    user_dict = {}

    for item in list_dir:
        if os.path.isfile(item) and ".http" in item:
            f = open(item)
            lines = f.readlines()
            for line in lines:
                ls = line.split()
                mac = ls[2]
                try:
                    if mac not in user_dict:
                        idx_alpha = len(user_dict)
                        user_dict[mac] = "USER."+alphabet[idx_alpha]
                except Exception as e:
                    print user_dict
                    pause()

            f.close()

    print len(user_dict)
    exit()

    for item in list_dir:
        if os.path.isfile(item) and ".http" in item:
            f = open(item)
            lines = f.readlines()
            for i, line in enumerate(lines):
                mac = line.split()[2]
                lines[i] = line.replace(mac, user_dict[mac])
            f.close()
            wf = open(item, "w")
            wf.writelines(lines)
            wf.close()


def find_dup():
    list_dir = os.listdir(os.getcwd())

    for line in list_dir:
        if os.path.isfile(line) and ".http" in line:
            f = open(line)
            lines = f.readlines()
            d = defaultdict(list)
            for k, va in [(v, i) for i, v in enumerate(lines)]:
                d[k].append(va)

            for x in d.items():
                if int(x[0].split()[3]) > 1000000 and len(x[1]) > 1:
                    print line
                    print x
            pause()


def rename_type():
    list_dir = os.listdir(os.getcwd())
    type_dict = {}
    for item in list_dir:
        if os.path.isfile(item) and ".http" in item:
            f = open(item)
            lines = f.readlines()
            for line in lines:
                content_type = line.split()[4]
                if content_type not in type_dict:
                    if "video/" in content_type:
                        v = "video"
                    elif "audio/" in content_type:
                        v = "audio"
                    elif "image/" in content_type:
                        v = "image"
                    elif "text" in content_type:
                        v = "text"
                    elif "application" in content_type:
                        v = "application"
                    elif "other" in content_type:
                        v = "other"
                    else:
                        # print content_type
                        v = "other"
                    type_dict[content_type] = v

    for item in list_dir:
        if os.path.isfile(item) and ".http" in item:
            f = open(item)
            lines = f.readlines()
            for i, line in enumerate(lines):
                content_type = line.split()[4]
                lines[i] = line.replace(content_type, type_dict[content_type])
            f.close()
            wf = open(item, "w")
            wf.writelines(lines)
            wf.close()


def sort_by_time():
    list_dir = os.listdir(os.getcwd())
    for item in list_dir:
        if os.path.isfile(item) and ".http" in item:
            f = open(item)
            lines = f.readlines()
            lines.sort(key=lambda i: int(mktime(strptime(i[0:19], "%Y-%m-%d %H:%M:%S"))))
            f.close()
            wf = open(item, "w")
            wf.writelines(lines)
            wf.close()


if __name__ == '__main__':
    #reassemble_from_date()
    rename_user()
    #rename_type()
    #find_dup()
    #sort_by_time()
