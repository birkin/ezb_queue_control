# -*- coding: utf-8 -*-

""" Handles illiad
    prepare-request, send-request, and evaluate request code. """

import json, os, sys
import requests
from dev_code import ezb_logger
from dev_code.tasks import task_manager


## prepare request ##

def prepare_illiad_request_data( data ):
    """ Returns data-dict required to call illiad_tunneler webservice. """
    assert sorted( data.keys() ) == [ u'flow', u'found_data', u'r_id' ], sorted( data.keys() )
    file_logger = ezb_logger.setup_logger()
    caller_data = _prep_caller_data( data, file_logger )
    file_logger.info( u'in caller_bd.prepare_illiad_request_data(); r_id, %s; caller_data, %s' % (data[u'r_id'], caller_data) )
    task_manager.determine_next_task(
        current_task=unicode(sys._getframe().f_code.co_name),
        data={
            u'illiad_caller_data':caller_data,
            u'found_data': data[u'found_data'],
            u'r_id': data[u'r_id']},
        logger=file_logger )
    return

def _prep_caller_data( data, file_logger ):
    """ Returns initial dict that will be enhanced.
        Note: much of the patron info is no longer acted upon by the api, since new-user registration
              now happens at landing page.
        Called by prepare_ill_request_data(). """
    ILLIAD_REMOTEAUTH_KEY = unicode( os.environ.get(u'ezb_ctl__ILLIAD_REMOTEAUTH_KEY') )
    parsed_openurl = _make_openurl_segment(
        original_openurl=data[u'found_data'][u'sfxurl'],
        r_id=data[u'r_id'],
        file_logger=file_logger )[u'parsed_openurl']
    caller_data_dict = {
        u'auth_key': ILLIAD_REMOTEAUTH_KEY,
        u'request_id': data[u'r_id'],
        u'first_name': data[u'found_data'][u'firstname'],  # originally used for new_user registration
        u'last_name': data[u'found_data'][u'lastname'],  # originally for new_user registration
        u'username': data[u'found_data'][u'eppn'],  # for login _and_ originally, new_user registration
        u'address': '',  # originally used for new_user registration
        u'email': data[u'found_data'][u'email'],  # originally used for new_user registration
        u'oclc_number': data[u'found_data'][u'wc_accession'],
        u'openurl': parsed_openurl,
        u'patron_barcode': data[u'found_data'][u'barcode'],
        u'patron_department': 'Unknown',  # originally used for new_user registration; was grabbed from patron-api 'dept'
        u'patron_status': data[u'found_data'][u'group'],  # originally used for new_user registration
        u'phone': u'',  # originally used for new_user registration
        u'volumes': data[u'found_data'][u'volumes'],  # perceived but not currently handled by dj_ill_submission
        }
    return caller_data_dict

def _make_openurl_segment( original_openurl, r_id, file_logger ):
    """ Returns parsed_openurl dict for illiad api call.
        Called by  _prep_caller_data(). """
    file_logger.info( u'in caller_ill._make_openurl_segment(); r_id, %s; original_openurl, %s' % (r_id, original_openurl) )
    temp = original_openurl[ original_openurl.find( u'serialssolutions.com/?' ) + 22 : ]  # TODO: change this to use the urlparse library
    parsed_openurl = temp.replace( u'genre=unknown', u'genre=book' )
    file_logger.info( u'in caller_ill._make_openurl_segment(); r_id, %s; parsed_openurl, %s' % (r_id, parsed_openurl) )
    return {
        u'original_openurl': original_openurl,
        u'parsed_openurl': parsed_openurl }

## make request ##

def submit_illiad_request( data ):
    """ Returns illiad confirmation number after making request.
        Possible TODO: if this request fails initiate another self-task with a 5-minute wait. """
    ( ILLIAD_REQUEST_URL, file_logger, db_logger ) = _setup_illiad_submit( data )
    try:
        illiad_response_dict = _do_illiad_submit( url=ILLIAD_REQUEST_URL, illiad_caller_data=data[u'illiad_caller_data'], file_logger=file_logger, db_logger=db_logger, r_id=data[u'r_id'] )
    except Exception as e:
        _handle_illiad_submission_error( e, file_logger, db_logger, data[u'r_id'] )
    task_manager.determine_next_task(
        current_task=unicode(sys._getframe().f_code.co_name),
        data={ u'illiad_response_data': illiad_response_dict, u'illiad_caller_data': data[u'illiad_caller_data'], u'found_data': data[u'found_data'], u'r_id': data[u'r_id']},
        logger=file_logger )
    return

def _setup_illiad_submit( data ):
    """ Returns required variables and validates data-dict.
        Called by submit_illiad_request(). """
    ILLIAD_REQUEST_URL = unicode( os.environ.get(u'ezb_ctl__ILLIAD_REQUEST_URL') )
    assert sorted( data.keys() ) == [ u'found_data', u'illiad_caller_data', u'r_id' ], sorted( data.keys() )
    file_logger = ezb_logger.setup_logger()
    db_logger = ezb_logger.setup_db_logger()
    return ( ILLIAD_REQUEST_URL, file_logger, db_logger )

def _do_illiad_submit( url, illiad_caller_data, file_logger, db_logger, r_id ):
    """ Returns result of submission.
        Called by submit_illiad_request(). """
    headers = { u'Content-Type': u'application/x-www-form-urlencoded; charset=utf-8' }
    r = requests.post( url, data=illiad_caller_data, headers=headers, timeout=60, verify=False )
    json_response = r.text
    message=u'- in caller_ill._do_illiad_submit(); r_id, %s; json_response: %s' % ( r_id, json_response )
    file_logger.info( message )
    db_logger.update_log( message=message, message_importance=u'low' )
    illiad_response_dict = json.loads( json_response )
    return illiad_response_dict

def _handle_illiad_submission_error( e, file_logger, db_logger, r_id ):
    """ We want:
        - an email to go out notifying the admin that there has been an illiad-submission-error.
        - the current job to be put on the failed queue so it can be requeued when the problem is fixed.
        Called by submit_illiad_request(). """
    message=u'- in caller_ill._handle_illiad_submission_error(); r_id, %s; exception: %s' % ( r_id, unicode(repr(e)) )
    file_logger.error( message )
    db_logger.update_log( message=message, message_importance=u'high' )
    job = q.enqueue_call( func=u'dev_code.tasks.emailer.email_illid_error', args=(data,), timeout=30 )
    illiad_response_dict = { u'error_message': message }
    raise Exception( u'Error submitting illiad request. Error logged and admin emailed.' )
    return
