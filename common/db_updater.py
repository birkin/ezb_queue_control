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
        """ Not a task.
            Updates request status.
            Called _by_ task, so file_logger is passed in. """
        assert sorted( data.keys() ) == [ u'db_id', u'status' ]
        payload = { u'status': data[u'status'], u'db_id': data[u'db_id'] }
        r = requests.post( settings.UPDATE_STATUS_URL, data=payload, auth=(settings.DB_PRX_USERNAME, settings.DB_PRX_PASSWORD) )

        status_dict = {  # temp, for debugging
            u'settings.NEW_CHECK_URL': settings.UPDATE_STATUS_URL,
            u'r.content': r.content.decode( u'utf-8' ),
            u'r.status_code': r.status_code }
        self.file_logger.debug( u'in db_updater.update_request_status(); status_dict, %s' % pprint.pformat(status_dict) )

        return

    # end class DbUpdater()



# def update_history_note( data=None ):
#     """ Task.
#         Updates history table note field.
#         Called _as_ task, so no file_logger is passed in. """
#     ( file_logger, db_handler_instance ) = _setup_logger_and_dbhandler()
#     file_logger.debug( u'in tasks.db_updater.update_history_note(); r_id %s; updating history note' % data[u'r_id'] )
#     assert u'history_note_text' in data.keys(), Exception( u'no history_note_text key' )
#     #TODO
#     return


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
