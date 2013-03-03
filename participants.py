#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json

valid = set(['o', '○', '◯'])
invalid = set(['x', '×', ''])

# Note: http://www.kyotobus.jp/route/timetable/kana26/hanaseyamanoiemae.html
# 出町柳 => 花背山の家
# - 07:50 => 09:03
# - 10:00 => 11:14
# - 14:50 => 16:04
# 花背山の家 => 出町柳
# - 08:12 => 09:28
# - 11:22 => 12:38
# - 14:57 => 16:13
# - 18:07 => 19:23
# 面倒なので:
# - ご飯たべたその直後から講座できる，とします

sessions = [
    '3/18 午後', # 0
    '3/19 午前', # 1
    '3/19 午後', # 2
    '3/20 午前', # 3
    '3/20 午後', # 4
    '3/21 午前', # 5
    '3/21 午後', # 6
]

begin = [
    0,  # 3/18昼食
    1,  # 3/18夕食
    1,  # 3/18宿泊

    1,  # 3/19朝食
    2,  # 3/19昼食
    3,  # 3/19夕食
    3,  # 3/19宿泊

    3,  # 3/20朝食
    4,  # 3/20昼食
    5,  # 3/20夕食
    5,  # 3/20宿泊

    5,  # 3/21朝食
    6,  # 3/21昼食
    7,  # 3/21夕食
    7,  # 3/21宿泊
]

# participates = {}

for line in sys.stdin:
    if not line:
        continue
    line = line.split('|')
    if not line[1] or line[1].startswith('\'') or line[1].startswith('example'):
        continue
    name = line[1]
    participates = [(xo in valid) for xo in line[2:2 + 3 + 4 * 3]]
    for i, p in enumerate(participates):
        if p:
            b = sessions[begin[i]]
            if participates[-1]:
                e = sessions[-1]
            else:
                for j, q in reversed(list(enumerate(participates))):
                    if q:
                        e = sessions[begin[j]-1]
                        break
            print('        "{0}": {1},'.format(name, {"first": b, "last": e}).replace('\'', '"'))
            break


