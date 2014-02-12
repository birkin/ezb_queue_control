# -*- coding: utf-8 -*-

import datetime, json, pprint, sys
import requests


# def make_datetime_string():
#   """ Returns time-string like 'Wed Oct 23 14:49:38 EDT 2013'. """
#   import time
#   time_object = time.localtime(); assert type(time_object) == time.struct_time
#   time_string = time.strftime( u'%a %b %d %H:%M:%S %Z %Y', time_object )
#   return time_string

def make_error_string():
  """ Returns detailed error information for logging/debugging. """
  error_message = u'error-type - %s; error-message - %s; line-number - %s' % (
    sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )
  return error_message
