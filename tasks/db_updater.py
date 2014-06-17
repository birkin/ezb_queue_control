# -*- coding: utf-8 -*-

""" Handles updates to Request and History tables. """

import pprint, sys
import requests
from ezb_queue_control.common import ezb_logger
from ezb_queue_control.config import settings
from ezb_queue_control.tasks import task_manager


class DbUpdater( object ):
    """ Handles calls to update db proxy. """

    def __init__( self, file_logger ):
        """ Holds state. """
        self.file_logger = file_logger

    def update_request_status( self, data ):
        """ Updates request status.
            Called tasks.new_request_monitor.run_check_for_new(). """
        assert sorted( data.keys() ) == [ u'db_id', u'status' ]
        payload = { u'status': data[u'status'], u'db_id': data[u'db_id'] }
        r = requests.post( settings.UPDATE_STATUS_URL, data=payload, auth=(settings.DB_PRX_USERNAME, settings.DB_PRX_PASSWORD) )
        status_dict = {  # temp, for debugging
            u'settings.NEW_CHECK_URL': settings.UPDATE_STATUS_URL,
            u'r.content': r.content.decode( u'utf-8' ),
            u'r.status_code': r.status_code }
        self.file_logger.debug( u'in tasks.db_updater.update_request_status(); status_dict, %s' % pprint.pformat(status_dict) )
        return

    def make_initial_history_note( self, request_id ):
        """ Updates history note. """
        payload = { u'db_id': request_id, u'history_note': u'Processing started.' }
        r = requests.post( settings.UPDATE_HISTORY_URL, data=payload, auth=(settings.DB_PRX_USERNAME, settings.DB_PRX_PASSWORD) )
        status_dict = {  # temp, for debugging
            u'settings.NEW_CHECK_URL': settings.UPDATE_STATUS_URL,
            u'r.content': r.content.decode( u'utf-8' ),
            u'r.status_code': r.status_code }
        self.file_logger.debug( u'in tasks.db_updater.make_initial_history_note(); status_dict, %s' % pprint.pformat(status_dict) )
        return

    # end class DbUpdater()


def run_make_initial_history_note( data ):
    """ Task.
        Triggered by tasks.new_request_monitor.run_check_for_new() """
    assert sorted( data.keys() ) == [ u'found_data', u'request_id' ]
    file_logger = ezb_logger.setup_file_logger(settings.FILE_LOG_PATH, settings.LOG_LEVEL)
    db_updater = DbUpdater( file_logger )
    db_updater.make_initial_history_note( data[u'request_id'] )
    task_manager.determine_next_task(
        current_task=unicode(sys._getframe().f_code.co_name),
        data={ u'found_data': data[u'found_data'], u'request_id': data[u'request_id'] },
        logger=file_logger )
    return
