# -*- coding: utf-8 -*-

""" Handles check-for-new-request issues.
    Always calls itself at end; all other tasks started by task_manager.py """

import datetime, os, sys, time
from dev_code import db_handler, dev_utility_code, ezb_logger, dev_settings
from dev_code.tasks import db_updater, task_manager
from redis import Redis
from rq import Queue


queue_name = dev_settings.QUEUE_NAME
q = Queue( queue_name, connection=Redis() )  # for check_for_new(); the only task which itself puts a new job on the queue


def check_for_new():
    """ Checks for new requests.
        If record found, updates Request table status. """
    try:
        ( file_logger, db_logger, db_handler_instance ) = _setup_new_check()
        dict_list = _run_sql_check( file_logger, db_handler_instance )
        _make_logger_message( file_logger, db_logger, dict_list )
        if dict_list:
            _update_status( dict_list=dict_list, r_id=dict_list[0][u'id'], file_logger=file_logger )
            task_manager.determine_next_task( unicode(sys._getframe().f_code.co_name), data={u'found_data': dict_list[0], u'r_id': dict_list[0].get(u'id')}, logger=file_logger )
        job = q.enqueue_call( func=u'dev_code.tasks.new_request_monitor.check_for_new', args=(), timeout=30 )  # always check for new
        sleep_seconds = dev_settings.NEW_CHECK_FREQUENCY; file_logger.debug( u'in dev_code.new_request_monitor.py.check_for_new(); going to sleep' )
        time.sleep( sleep_seconds )
        file_logger.info( u'in dev_code.new_request_monitor.py.check_for_new(); done' )
        return
    except Exception as e:
        file_logger = ezb_logger.setup_logger()
        file_logger.error( u'in dev_code.new_request_monitor.py.check_for_new(); exception: %s' % unicode(repr(e)) )
        detail_message = dev_utility_code.make_error_string()
        file_logger.error( u'in dev_code.new_request_monitor.py.check_for_new(); detail_message: %s' % unicode(repr(detail_message)) )
        raise Exception( u'Error checking for new record.' )  # TODO: consider commenting this out so new-checks don't stop


def _setup_new_check():
    """ Sets up and returns logger & db-handler instances, and updates initial log-entries.
        Called by check_for_new() """
    file_logger = ezb_logger.setup_logger()
    db_logger = ezb_logger.setup_db_logger()
    db_handler_instance = db_handler.get_db_handler( file_logger )
    message = u'DevController session STARTING at %s; checking for request record...' % unicode(datetime.datetime.now())
    file_logger.info( message );
    db_logger.update_log( message=message, message_importance=u'high' )
    return ( file_logger, db_logger, db_handler_instance )




def _make_logger_message( file_logger, db_logger,  dict_list ):
    """ Sets logging message on initial record check.
        Called by check_for_new() """
    if len(dict_list) == 0:
        message = u'in dev_code.new_request_monitor.py.check_for_new(); no new request found; quitting'
    else:
        r_id = dict_list[0][u'id']
        message = u'in dev_code.new_request_monitor.py.check_for_new(); r_id %s; record found; data: %s' % ( r_id, dict_list )
    file_logger.info( message )
    db_logger.update_log( message, message_importance=u'high' )
    return


def _update_status( dict_list, r_id, file_logger ):
    """ Updates request table status.
        Not done as separate task to minimize chance of double-processing request. """
    data = {
        u'db_id': dict_list[0][u'id'],
        u'status': u'in_process' }
    db_updater.update_request_status( data=data, file_logger=file_logger )
    return
