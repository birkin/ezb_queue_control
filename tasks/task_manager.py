# -*- coding: utf-8 -*-

""" Handles next-task issues. """

import json, os, sys
import redis, rq
from types import InstanceType, NoneType
from ezb_queue_control.config import settings
from ezb_queue_control.common import utility_code


q = rq.Queue( settings.QUEUE_NAME, connection=redis.Redis() )


## determine_next_task() ##


def determine_next_task( current_task, data=None, logger=None ):
    """ Determines and calls next task.
        This is the logic-flow function. """
    try:
        _check_params( current_task, data, logger )
        next_task = None
        logger.debug( u'in tasks.task_manager.determine_next_task(); current_task: %s' % current_task )

        if current_task == u'check_for_new':  # new_request_monitor.py
            assert sorted( data.keys() ) == [ u'found_data', u'r_id' ], sorted( data.keys() )
            if len( data['found_data'] ) > 0:
                data[u'history_note_text'] = u'Processing started'
                next_task = u'ezb_queue_control.tasks.db_updater.update_history_note'

        elif current_task == u'update_history_note':  # db_updater.py
            assert u'history_note_text' in data.keys(), u'expected key history_note_text not found'
            if data[u'history_note_text'] == u'Processing started':  # new_request_monitor.py
                del( data[u'history_note_text'] ); assert sorted( data.keys() ) == [ u'found_data', u'r_id' ]
                next_task = u'ezb_queue_control.tasks.task_manager.determine_flow'
            elif data[u'history_note_text'] == u'no_valid_bd_string':  # caller_bd.prepare_bd_request_data() failed on string-search
                del( data[u'history_note_text'] ); assert sorted( data.keys() ) == [ u'flow', u'found_data', u'r_id' ]
                position = data[u'flow'].index( u'bd' )
                next_in_flow = data[u'flow'][position + 1]
                if next_in_flow == u'illiad':
                    next_task = u'ezb_queue_control.tasks.caller_ill.prepare_illiad_request_data'

        elif current_task == u'determine_flow':  # task_manager.py
            assert sorted( data.keys() ) == [u'flow', u'found_data', u'r_id'], sorted( data.keys() )
            if data[u'flow'][0] == u'bd':
                next_task = u'ezb_queue_control.tasks.caller_bd.prepare_bd_request_data'
            elif data[u'flow'][0] == u'illiad':
                next_task = u'ezb_queue_control.tasks.tunneler_runners.run_illiad'
            else:
                next_task = u'ezb_queue_control.tasks.tunneler_runners.run_inrhode'  # not possible as of 2014-01, but determine_flow() can change based on policy.

        elif current_task == u'prepare_bd_request_data':  # caller_bd.py
            assert sorted( data.keys() ) == [ u'bd_caller_data', u'flow', u'found_data', u'r_id' ], sorted( data.keys() )
            if data[u'bd_caller_data'][u'good_to_go'] == True:
                del( data[u'bd_caller_data']['good_to_go'] )  # now bd_caller_data is exactly what the api needs
                data[u'bd_tunneler_url'] = settings.BD_API_URL  # TODO: this is dumb; request_bd_item() should grab this
                next_task = u'ezb_queue_control.tasks.caller_bd.request_bd_item'
            else:  # caller_bd.prepare_bd_request_data() failed on string-search
                del( data[u'bd_caller_data'] )
                data[u'history_note_text'] = u'no_valid_bd_string'
                next_task = u'ezb_queue_control.tasks.caller_bd.update_history_note'

        elif current_task == u'request_bd_item':  # caller_bd.py
            assert sorted( data.keys() ) == [ u'bd_tunneler_response', u'flow', u'found_data', u'r_id' ], sorted( data.keys() )
            next_task = u'ezb_queue_control.tasks.db_updater.update_bd_history_status'

        elif current_task == u'update_bd_history_status':  # db_updater.py
            assert sorted( data.keys() ) == [ u'bd_tunneler_response', u'flow', u'found_data', u'r_id' ], sorted( data.keys() )
            if data[u'bd_tunneler_response'][u'bd_confirmation_code'] == u'':
                position = data[u'flow'].index( u'bd' )
                next_in_flow = data[u'flow'][position + 1]
                if next_in_flow == u'illiad':
                    del( data['bd_tunneler_response'] )
                    next_task = u'ezb_queue_control.tasks.caller_ill.prepare_illiad_request_data'
            # if len( data[u'bd_tunneler_response'][u'bd_confirmation_code'] ) > 0:  # success!
            #     data[u'request_status'] = u'processed'
            #     next_task = u'ezb_queue_control.tasks.update_request_status' --> then email work

        elif current_task == u'prepare_illiad_request_data':  # caller_ill.py
            assert sorted( data.keys() ) == [ u'found_data', u'illiad_caller_data', u'r_id' ], sorted( data.keys() )
            next_task = u'ezb_queue_control.tasks.caller_ill.submit_illiad_request'

        # elif current_task == u'submit_illiad_request':  # caller_ill.py
        #     assert sorted( data.keys() ) == [ u'found_data', u'illiad_caller_data', u'illiad_response_data', u'r_id' ], sorted( data.keys() )

        else:
            message = u'in task_manager.determine_next_task(); no next task selected for current_task, %s; data, %s' % (current_task, data)
            logger.info( message )

        logger.debug( u'in tasks.task_manager.determine_next_task(); next_task: %s' % next_task )
        if next_task:
            job = q.enqueue_call ( func=u'%s' % next_task, args = (data,), timeout=30 )
        return

    except Exception as e:
        detail_message = utility_code.make_error_string()
        logger.error( u'in tasks.task_manager.determine_next_task(); detail_message: %s' % unicode(repr(detail_message)) )
        sys.exit()


def _check_params( current_task, data, logger ):
    """ Validates determine_next_task() inputs.
        Called by determine_next_task(). """
    assert type( current_task ) == unicode, Exception( u'current_task must be unicode; it is: %s' % type(current_task) )
    assert type( data ) in [ dict, NoneType ], Exception( u'data of incorrect type; it is: %s' % type(data) )
    assert type( logger ) == InstanceType, Exception( u'logger of incorrect type; it is: %s' % type(logger) )
    return True


## TASK: determine_flow() ##


def determine_flow( data ):
    """ Determines services to call and their order -- and sets next_service. """
    _validate_determine_flow_data( data )
    file_logger = ezb_logger.setup_logger()
    if len( data[u'found_data'][u'volumes'] ) > 0:
        flow = [ u'illiad' ]
    elif len( data[u'found_data'][u'isbn'] ) > 0:
        flow = [ u'bd', u'ir', u'illiad' ]  # changed on 2012-09-05 at request of BH from 2012-04-02 email
    else:
        flow = [ u'bd', u'illiad' ]  # bd tuneller-runner will see if it has valid data for a bd request
    file_logger.info( u'in task_manager.determine_flow(); r_id, %s; flow, %s' % (data[u'r_id'], flow) )
    determine_next_task( unicode(sys._getframe().f_code.co_name), data={u'found_data': data[u'found_data'], u'r_id': data[u'r_id'], u'flow': flow}, logger=file_logger )
    return flow


def _validate_determine_flow_data( data ):
    """ Validates data send to above def. """
    assert data.keys() == [u'found_data', u'r_id'], data.keys()
    for key in [ u'isbn', u'volumes' ]:
        assert key in data[u'found_data'].keys(), ( key, data[u'found_data'].keys() )
    return
