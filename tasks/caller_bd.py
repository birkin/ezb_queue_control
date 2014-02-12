# -*- coding: utf-8 -*-

""" Handles borrowdirect
    prepare-request, and make-request code. """

import json, os, sys
import requests
from dev_code import ezb_logger, dev_settings
from dev_code.tasks import task_manager


## prepare request ##


def prepare_bd_request_data( data ):
    """ Returns data-dict required to call borrowdirect_tunneler webservice. """
    assert sorted( data.keys() ) == [u'flow', u'found_data', u'r_id'], sorted( data.keys() )
    file_logger = ezb_logger.setup_logger()
    caller_data = _make_initial_data_dict( data )
    search_type = _determine_search_type( data, file_logger )
    if search_type == u'isbn':
        caller_data[u'isbn'], caller_data[u'good_to_go'] = data[u'found_data'][u'isbn'], True
    else:  # u'string'
        caller_data = _make_search_strings( data=data, caller_data=caller_data, openurl_parser_url=dev_settings.OPENURL_PARSER_URL, file_logger=file_logger )
    file_logger.info( u'in caller_bd.prepare_bd_request_data(); r_id, %s; caller_data, %s' % (data[u'r_id'], caller_data) )
    task_manager.determine_next_task( unicode(sys._getframe().f_code.co_name), data={u'bd_caller_data':caller_data, u'flow': data[u'flow'], u'found_data': data[u'found_data'], u'r_id': data[u'r_id']}, logger=file_logger )
    return


def _make_initial_data_dict( data ):
    """ Returns initial dict that will be enhanced.
        Called by prepare_bd_request_data()"""
    caller_data_dict = {
        u'good_to_go': False,  # not really sent to borrowdirect tunneler -- just a processing flag
        u'api_authorization_code': dev_settings.BD_API_AUTHORIZATION_CODE,
        u'api_identity': dev_settings.BD_API_IDENTITY,
        u'university': dev_settings.BD_API_UNIVERSITY,
        u'user_barcode': data[u'found_data'][u'barcode'],
        u'command': u'request',
        }
    return caller_data_dict


def _determine_search_type( data, file_logger ):
    """ Returns whether search is a string-search or isbn-search.
        Called by prepare_bd_request_data()"""
    isbn = data[u'found_data'][u'isbn']
    if len( isbn ) > 0:
      search_type = u'isbn'
    else:
      search_type = u'string'
    file_logger.info( u'in caller_bd._determine_search_type(); r_id, %s; search_type, %s' % (data[u'r_id'], search_type) )
    return search_type


def _make_search_strings( data, caller_data, openurl_parser_url, file_logger ):
    """ Returns dict of string values for borrowdirect_tunneler string-search.
        Called by prepare_bd_request_data()"""
    try:
        payload = { u'db_wc_url': data[u'found_data'][u'sfxurl'] }  # sfxurl is the worldcat_openurl_string
        r = requests.get( openurl_parser_url, params=payload, verify=False )
        worldcat_openurl_parsed_response = r.content.decode( u'utf-8', u'replace' )
        file_logger.info( u'in caller_bd._make_search_string(); r_id, %s; worldcat_openurl_parsed_response, %s' % (data[u'r_id'], worldcat_openurl_parsed_response) )
        d = json.loads( worldcat_openurl_parsed_response )
        caller_data[u'good_to_go'], caller_data[u'title'], caller_data[u'author'], caller_data[u'date'] = True, d[u'response'][u'bd_title'], d[u'response'][u'bd_author'], d[u'response'][u'bd_date']
    except Exception as e:
        file_logger.error( u'in caller_bd._make_search_string(); r_id, %s; error, %s' % (data[u'r_id'], unicode(repr(e))) )
    return caller_data


## make request ##


def request_bd_item( data ):
    """ Hits our borrowdirect-tunneler-webservice.
        Returns 'found', 'requestable', and (on success) 'bd_confirmation_code'. """
    ( file_logger, bd_tunneler_response ) = _setup_bd_request( data )
    try:
        _make_bd_request( data, bd_tunneler_response, file_logger )
    except Exception as e:
        file_logger.error( u'in caller_bd.request_item(); r_id, %s; error, %s' % (data[u'r_id'], unicode(repr(e))) )
        pass  # must not bring processing to a halt
    file_logger.info( u'in caller_bd.request_bd_item(); r_id, %s; bd_tunneler_response, %s' % (data[u'r_id'], bd_tunneler_response) )
    task_manager.determine_next_task( unicode(sys._getframe().f_code.co_name), data={u'bd_tunneler_response':bd_tunneler_response, u'flow': data[u'flow'], u'found_data': data[u'found_data'], u'r_id': data[u'r_id']}, logger=file_logger )
    return


def _setup_bd_request( data ):
    """ Returns file_logger and initialized bd_tunneler_response dict -- and validates data-keys.
        Called by request_bd_item(). """
    assert sorted( data.keys() ) == [ u'bd_caller_data', u'bd_tunneler_url', u'flow', u'found_data', u'r_id'], sorted( data.keys() )
    file_logger = ezb_logger.setup_logger()
    bd_tunneler_response = { u'found': u'', u'requestable': u'', u'bd_confirmation_code': u'', u'temp_status_flag': u'' }
    return ( file_logger, bd_tunneler_response )


def _make_bd_request( data, bd_tunneler_response, file_logger ):
    """ Returns output from bd request.
        Called by request_bd_item(). """
    r = requests.post( data['bd_tunneler_url'], data=data[u'bd_caller_data'], verify=False )
    ( status_code, output ) = ( r.status_code, r.content.decode( u'utf-8', u'replace') )
    file_logger.debug( u'in caller_bd._make_bd_request(); r_id, %s; r.content, %s; r.status_code, %s' % (data[u'r_id'], output, status_code) )
    if status_code == 403:
        bd_tunneler_response[u'temp_status_flag'] = u'could_not_process'
    else:
        d = json.loads( output )
        for key in [ u'found', u'requestable', u'bd_confirmation_code' ]:
            bd_tunneler_response[key] = d[u'response'][key]
    return bd_tunneler_response




# updateHistoryTable()

# requestItem()

# updateHistoryTable()

# on success return the confirmation-number
