# -*- coding: utf-8 -*-

""" Starts ezb processing
    Assumes rq worker(s) started from ezb_queue_control parent directory.
    Assumes this file is called from ezb_queue_control parent directory.
    """

import os
import redis, rq
from ezb_queue_control.common import ezb_logger
from ezb_queue_control.config import settings


file_logger = ezb_logger.setup_file_logger( settings.FILE_LOG_DIR, settings.LOG_LEVEL )
file_logger.info( u'STARTING FILE_LOGGER')

q = rq.Queue( settings.QUEUE_NAME, connection=redis.Redis() )

job = q.enqueue_call(
  func=u'ezb_queue_control.tasks.new_request_monitor.check_for_new',
  kwargs = {} )
