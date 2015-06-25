# -*- coding: utf-8 -*-
import sys
import traceback


def format_traceback():
    etype, value, tb = sys.exc_info()
    ret = ''.join(traceback.format_exception(etype, value, tb))
    return '<pre>%s</pre>' % ret
