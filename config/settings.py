# -*- coding: utf-8 -*-

import os


# file-logger
FILE_LOG_DIR = unicode( os.environ.get(u'ezb_ctl__FILE_LOG_DIR') )

## db-logger
DB_LOG_URL = unicode( os.environ.get(u'ezb_ctl__DB_LOG_URL') )
DB_LOG_USERNAME = unicode( os.environ.get(u'ezb_ctl__DB_LOG_USERNAME') )  # basic-auth
DB_LOG_PASSWORD = unicode( os.environ.get(u'ezb_ctl__DB_LOG_PASSWORD') )  # basic-auth

## both loggers
LOG_LEVEL = unicode( os.environ.get(u'ezb_ctl__LOG_LEVEL') )

## borrowdirect
BD_API_URL = unicode( os.environ.get(u'ezb_ctl__BD_API_URL') )  # task_manager.py -- TODO: use this from caller_bd.py
BD_API_AUTHORIZATION_CODE = unicode( os.environ.get(u'ezb_ctl__BD_API_AUTHORIZATION_CODE') )
BD_API_IDENTITY = unicode( os.environ.get(u'ezb_ctl__BD_API_IDENTITY') )
BD_API_UNIVERSITY = unicode( os.environ.get(u'ezb_ctl__BD_API_UNIVERSITY') )

## illiad
# os.environ calls made directly from tasks/caller_ill.py

## general
OPENURL_PARSER_URL = unicode( os.environ.get(u'ezb_ctl__OPENURL_PARSER_URL') )
QUEUE_NAME = unicode( os.environ.get(u'ezb_ctl__QUEUE_NAME') )  # new_request_monitor.py, start.py, task_manager.py
NEW_CHECK_FREQUENCY = int( unicode(os.environ.get(u'ezb_ctl__NEW_CHECK_FREQUENCY')) )  # new_request_monitor.py; used for time.sleep( seconds )
