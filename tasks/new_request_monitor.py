# -*- coding: utf-8 -*-

""" Handles check-for-new-request issues.
    Always calls itself at end; all other tasks started by task_manager.py """

import datetime, os, pprint, sys, time
import redis, requests, rq
from ezb_queue_control.common import ezb_logger, utility_code
from ezb_queue_control.common.db_updater import DbUpdater
from ezb_queue_control.config import settings
from ezb_queue_control.tasks import task_manager


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
    ( file_logger, db_logger ) = ( ezb_logger.setup_file_logger(settings.FILE_LOG_PATH, settings.LOG_LEVEL), ezb_logger.setup_db_logger(settings.DB_LOG_URL, settings.DB_LOG_URL_KEY, settings.LOG_LEVEL, file_logger) )
    monitor = Monitor( file_logger, db_logger )
    db_updater = DbUpdater( file_logger )
    result_dicts = monitor.check_for_new()
    if result_dicts:
        for result_dict in result_dicts:
            update_data = { u'db_id': result_dict[u'db_id'], u'status': u'in_process' }
            db_updater.update_request_status( data=update_data )  # done here instead of as separate job to minimize chance of multiple-processing
            q.enqueue_call( func=u'ezb_queue_control.tasks.db_updater.run_make_initial_history_note', kwargs={ u'found_data': result_dict, u'request_id': result_dict[u'db_id'] }, timeout=30 )  # always check for new
    return
