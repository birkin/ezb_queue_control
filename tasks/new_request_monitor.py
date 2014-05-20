# -*- coding: utf-8 -*-

""" Handles check-for-new-request issues.
    Always calls itself at end; all other tasks started by task_manager.py """

import datetime, os, pprint, sys, time
import redis, requests, rq
from ezb_queue_control.config import settings
from ezb_queue_control.common import ezb_logger, utility_code
from ezb_queue_control.tasks import db_updater, task_manager


class Monitor( object ):
    """ Checks for new requests. """

    def __init__( self, file_logger, db_logger ):
        """ Holds state. """
        self.file_logger = file_logger
        self.db_logger = db_logger

    def check_for_new( self ):
        """ Checks for new requests.
            Returns list of dicts.
            Called by cron, or, for developement, tasks/start.py """
        self.file_logger.debug( u'in new_request_monitor.check_for_new(); starting.' )
        self._log_start_messages()
        result_dicts = self._query_new()
        self._log_check_result( result_dicts )
        return result_dicts

    def _log_start_messages( self ):
        """ Creates initial db-log-entry.
            Called by check_for_new() """
        db_log_message = u'QController session STARTING at %s; checking for request record...' % unicode( datetime.datetime.now() )
        self.file_logger.info( db_log_message )
        self.db_logger.update_log( message=db_log_message, message_importance=u'high' )
        return

    def _query_new( self ):
        """ Sends request to db-proxy for json data.
            Returns empty or populated list of result-dicts. """
        r = requests.get( settings.NEW_CHECK_URL, auth=(settings.DB_PRX_USERNAME, settings.DB_PRX_PASSWORD) )
        status_dict = {  # temp, for debugging
            u'settings.NEW_CHECK_URL': settings.NEW_CHECK_URL,
            u'r.content': r.content.decode( u'utf-8' ),
            u'r.status_code': r.status_code }
        self.file_logger.debug( u'in new_request_monitor._query_new(); status_dict, %s' % pprint.pformat(status_dict) )
        json_dict = r.json()
        result_dicts = json_dict[u'result']
        return result_dicts

    def _log_check_result( self, result_dicts ):
        """ Updates db-log with check result.
            Called by check_for_new() """
        if len(result_dicts) == 0:
            message = u'no new request found; quitting'
        else:
            message = u'%s new requests found' % len(result_dicts)
        self.file_logger.info( u'in new_request_monitor._log_check_result(); %s' % message )
        self.db_logger.update_log( message=message, message_importance=u'high' )
        return

    # end class Monitor()


def run_check_for_new():
    """ Caller for Monitor.check_for_new().
        Called by job-queue.
        Note: aside from start.py, this is the only task which itself puts a new job on the queue. """
    q = rq.Queue( settings.QUEUE_NAME, connection=redis.Redis() )
    file_logger = ezb_logger.setup_file_logger( settings.FILE_LOG_PATH, settings.LOG_LEVEL )
    db_logger = ezb_logger.setup_db_logger( settings.DB_LOG_URL, settings.DB_LOG_URL_KEY, settings.LOG_LEVEL, file_logger )
    monitor = Monitor( file_logger, db_logger )
    result_dicts = monitor.check_for_new()
    if result_dicts:
        for result_dict in result_dicts:
            data = { u'db_id': result_dict[u'db_id'], u'status': u'in_process' }
            db_updater.update_request_status( data=data, file_logger=file_logger )  # done here instead of as separate job to minimize chance of multiple-processing
            q.enqueue_call( func=u'ezb_queue_control.tasks.db_updater.update_history_note', kwargs={ u'found_data': result_dict, u'request_id': result_dict[u'db_id'] }, timeout=30 )  # always check for new
    return



# def check_for_new():
#     """ Checks for new requests.
#         If record found, updates Request table status.
#         Updates db-logger.
#         Called by start.py and this function itself. """
#     ( file_logger, db_logger ) = _setup_new_check()
#     result_dict = _query_new( file_logger )
#     _make_logger_message( file_logger, db_logger, result_dict )
#     if result_dict:
#         _update_status( result_dict=result_dict, file_logger=file_logger )
#         task_manager.determine_next_task( unicode(sys._getframe().f_code.co_name), data={u'found_data': result_dict, u'r_id': result_dict.get(u'id')}, logger=file_logger )
#     job = q.enqueue_call( func=u'ezb_queue_control.tasks.new_request_monitor.check_for_new', args=(), timeout=30 )  # always check for new
#     sleep_seconds = settings.NEW_CHECK_FREQUENCY; file_logger.debug( u'in new_request_monitor.check_for_new(); going to sleep' )
#     time.sleep( sleep_seconds )
#     file_logger.info( u'in new_request_monitor.check_for_new(); done' )
#     return


# def _setup_new_check():
#     """ Sets up and returns logger & db-handler instances, and updates initial log-entries.
#         Called by check_for_new() """
#     file_logger = ezb_logger.setup_file_logger( settings.FILE_LOG_PATH, settings.LOG_LEVEL )
#     db_logger = ezb_logger.DB_Logger(
#         settings.DB_LOG_URL,
#         settings.DB_LOG_URL_KEY,
#         settings.LOG_LEVEL,
#         file_logger )
#     file_logger.debug( u'in new_request_monitor._setup_new_check(); db_logger.log_id, %s' % db_logger.log_id )
#     message = u'QController session STARTING at %s; checking for request record...' % unicode( datetime.datetime.now() )
#     file_logger.info( message )
#     db_logger.update_log( message=message, message_importance=u'high' )
#     return ( file_logger, db_logger )


# def _query_new( file_logger ):
#     """ Sends request to db-proxy for json data.
#         Returns empty or populated result-dict. """
#     r = requests.get( settings.NEW_CHECK_URL, auth=(settings.DB_PRX_USERNAME, settings.DB_PRX_PASSWORD) )
#     status_dict = {  # temp, for debugging
#         u'settings.NEW_CHECK_URL': settings.NEW_CHECK_URL,
#         u'r.content': r.content.decode( u'utf-8' ),
#         u'r.status_code': r.status_code
#         }
#     file_logger.debug( u'in new_request_monitor._query_new(); status_dict, %s' % pprint.pformat(status_dict) )
#     json_dict = r.json()
#     result_dict = json_dict[u'result']
#     return result_dict


# def _make_logger_message( file_logger, db_logger,  result_dict ):
#     """ Sets logging message on initial record check.
#         Called by check_for_new() """
#     if len(result_dict) == 0:
#         message = u'in new_request_monitor.py.check_for_new(); no new request found; quitting'
#     else:
#         r_id = result_dict[u'db_id']
#         message = u'in new_request_monitor.py.check_for_new(); r_id %s; record found; data: %s' % ( r_id, result_dict )
#     file_logger.info( message )
#     db_logger.update_log( message, message_importance=u'high' )
#     return


# def _update_status( result_dict, file_logger ):
#     """ Updates request table status.
#         Not done as separate task to minimize chance of double-processing request. """
#     data = {
#         u'db_id': result_dict[u'db_id'],
#         u'status': u'in_process' }
#     db_updater.update_request_status( data=data, file_logger=file_logger )
#     return
