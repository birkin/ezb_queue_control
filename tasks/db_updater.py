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


def run_make_initial_history_note( found_data, request_id ):
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




# def update_bd_history_status( data ):
#     """ Task.
#         Updates history table with bd attempt result. """
#     assert sorted( data.keys() ) == [ u'bd_tunneler_response', u'flow', u'found_data', u'r_id' ], sorted( data.keys() )
#     ( file_logger, db_handler_instance ) = _setup_logger_and_dbhandler()
#     history_status = _determine_bd_history_status( data[u'bd_tunneler_response'] )
#     #TODO
#     return

# def _determine_bd_history_status( bd_tunneler_response_dict ):
#     """ Helper.
#         Returns history_status info.
#         Called by update_bd_history_status(). """
#     history_status = {}
#     if len( bd_tunneler_response_dict[u'bd_confirmation_code'] ) > 0:  # success!
#         ( history_status[u'result'], history_status[u'number'] ) = ( u'Request_Successful', data[u'bd_tunneler_response'][u'bd_confirmation_code'] )
#     elif bd_tunneler_response_dict[u'found'] == False:
#         ( history_status[u'result'], history_status[u'number'] ) = ( u'not_found', u'not_applicable' )
#     elif bd_tunneler_response_dict[u'found'] == True and bd_tunneler_response_dict[u'requestable'] == False:
#         ( history_status[u'result'], history_status[u'number'] ) = ( u'not_requestable', u'not_applicable' )
#     else:
#         ( history_status[u'result'], history_status[u'number'] ) = ( u'could_not_process', u'not_applicable' )
#     return history_status


# ## General helpers ##


# def _setup_logger_and_dbhandler():
#     """ Helper.
#         Returns file_logger and db_handler_instance.
#         Called by task update_history_note(), and task update_bd_history_status() """
#     #TODO- this will no longer work with non-sql code; fix.
#     file_logger = ezb_logger.setup_file_logger( settings.FILE_LOG_PATH, settings.LOG_LEVEL )
#     db_handler_instance = db_handler.get_db_handler( file_logger )
#     return ( file_logger, db_handler_instance )
