#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import logging.handlers
from os.path import expanduser, exists
import sys


def pp(obj):
    if isinstance(obj, list) or isinstance(obj, dict):
        orig = json.dumps(obj, indent=4)
        print(eval("u'''{0}'''".format(orig)).encode('utf-8'))
    else:
        print(obj)


def logger():
    log = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s\t%(pathname)s\t%(funcName)s\t'
                                  '%(lineno)d\t%(levelname)s\t: %(message)s')
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    handler = logging.handlers.RotatingFileHandler('logger.log')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

log = logger()


if __name__ == '__main__':
    log.debug('hoge')
    log.info('hoge')
    log.warning('hoge')
    log.error('hoge')
    try:
        1 / 0
    except:
        log.exception('AAA')
