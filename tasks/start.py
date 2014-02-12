# -*- coding: utf-8 -*-

""" Starts ezb processing
    Assumes rq worker(s) started from ezborrow_python_code directory.
    Assumes this file is called from ezborrow_python_code directory.
    """

import os
from dev_code import ezb_logger, dev_settings
from redis import Redis
from rq import Queue


file_logger = ezb_logger.setup_logger()
file_logger.info( u'STARTING FILE_LOGGER')

queue_name = dev_settings.QUEUE_NAME
q = Queue( queue_name, connection=Redis() )

job = q.enqueue_call(
  func=u'dev_code.tasks.new_request_monitor.check_for_new',
  args = (),
  timeout = 30
  )

