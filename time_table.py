#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json


def read_input_file(filename):
    input_data = json.loads(filename)



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: time_table.py input.json', file=sys.stderr)
        exit(-1)

