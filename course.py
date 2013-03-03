#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import json

for line in sys.stdin:
    if not line:
        continue
    line = line.split('|')
    name = line[1]
    applicants = re.split(r'[, ]+', line[-2]) if line[-2] else []
    applicants.extend(re.split(r'[, ]+', line[-3]) if line[-3] else [])
    times = [int(t) for t in re.split(r'[^0-9]+', line[3]) if t]
    title = line[2]
    d = {"name": name, "applicants": applicants, "times": times, "title": title}
    print('        {0},'.format(eval(json.dumps(d))).replace('\'', '"'))
