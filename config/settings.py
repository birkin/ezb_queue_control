# -*- coding: utf-8 -*-

import os


# file-logger
FILE_LOG_PATH = unicode( os.environ[u'ezb_ctl__FILE_LOG_PATH'] )

## db-logger
DB_LOG_URL = unicode( os.environ[u'ezb_ctl__DB_LOG_URL'] )
DB_LOG_URL_KEY = unicode( os.environ[u'ezb_ctl__DB_LOG_URL_KEY'] )

## db proxy
NEW_CHECK_URL = unicode( os.environ[u'ezb_ctl__DB_NEW_REQUESTS_URL'] )
UPDATE_STATUS_URL = unicode( os.environ[u'ezb_ctl__DB_UPDATE_STATUS_URL'] )
DB_PRX_USERNAME = unicode( os.environ[u'ezb_ctl__DB_AUTH_USERNAME'] )
DB_PRX_PASSWORD = unicode( os.environ[u'ezb_ctl__DB_AUTH_PASSWORD'] )

## both loggers
LOG_LEVEL = unicode( os.environ[u'ezb_ctl__LOG_LEVEL'] )

## borrowdirect
BD_API_URL = unicode( os.environ[u'ezb_ctl__BD_API_URL'] )  # task_manager.py -- TODO: use this from caller_bd.py
BD_API_AUTHORIZATION_CODE = unicode( os.environ[u'ezb_ctl__BD_API_AUTHORIZATION_CODE'] )
BD_API_IDENTITY = unicode( os.environ[u'ezb_ctl__BD_API_IDENTITY'] )
BD_API_UNIVERSITY = unicode( os.environ[u'ezb_ctl__BD_API_UNIVERSITY'] )

## illiad
# os.environ calls made directly from tasks/caller_ill.py

## general
OPENURL_PARSER_URL = unicode( os.environ[u'ezb_ctl__OPENURL_PARSER_URL'] )
QUEUE_NAME = unicode( os.environ[u'ezb_ctl__QUEUE_NAME'] )  # new_request_monitor.py, start.py, task_manager.py
NEW_CHECK_FREQUENCY = int( unicode(os.environ[u'ezb_ctl__NEW_CHECK_FREQUENCY')] )  # new_request_monitor.py; used for time.sleep( seconds )
