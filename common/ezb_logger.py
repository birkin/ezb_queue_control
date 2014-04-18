# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, random
import requests
from ezb_queue_control import common
# from ezb_queue_control.config import settings


def setup_file_logger( file_log_dir, file_log_level ):
    """ Returns a logger to write to a file.
        Called by caller_ill.py """
    filename = u'%s/dev_ezb.log' % file_log_dir
    formatter = logging.Formatter( u'[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s' )
    logger = logging.getLogger( u'ezb_logger' )
    level_dict = { u'debug': logging.DEBUG, u'info':logging.INFO }
    logger.setLevel( level_dict[file_log_level] )
    file_handler = logging.handlers.RotatingFileHandler( filename, maxBytes=(5*1024*1024), backupCount=1 )
    file_handler.setFormatter( formatter )
    logger.addHandler( file_handler )
    return logger


def setup_db_logger():
    """ Returns a db_logger_instance that'll post json to a db-logger webservice.
        Called by caller_ill.py """
    db_logger = DB_Logger( settings.DB_LOG_URL, settings.DB_LOG_URL_KEY )
    return db_logger


class DB_Logger(object):
    """ Sends message to a centralized ezb db-logger. """

    def __init__( self, url, key, log_level, file_logger, log_id=None ):
        """ Holds state. """
        self.url = url
        self.key = key
        self.log_level = log_level
        self.file_logger = file_logger
        self.log_id = self.set_log_id( log_id )

    def set_log_id( self, log_id ):
        """ Sets instance log_id if given one, otherwise creates a temp one. """
        if log_id == None:
            self.log_id = u'%s - %s' % ( unicode(datetime.datetime.now()), random.randint(1111, 9999) )
        return

    def update_log( self, message, message_importance ):
        """ Takes message and message_importance strings.
            Sends message to ezb db-logger api if it's important enough.
            Returns status_code dict.
            Called by various functions. """
        self.file_logger.debug( u'in ezb_logger.update_log(); starting' )
        if self._worthwhile_check( message_importance ) == False:
            return
        payload = { u'message': message, u'identifier': self.log_id, u'key': self.key }
        r = requests.post( self.url, data=payload )
        self.file_logger.debug( u'in ezb_logger.update_log(); r.content, %s' % r.content.decode(u'utf-8') )
        status_dict = { u'update_log_status_code': r.status_code, u'message': message }
        self.file_logger.debug( u'in ezb_logger.update_log(); status_dict, %s' % pprint.pformat(status_dict) )
        return

    def _worthwhile_check( self, message_importance ):
        """ Takes u'high/low' message_importance string.
            Determines whether to log, given the message-importance and log-level.
            Returns boolean.
            Called by update_log(). """
        var = False
        if message_importance == u'high':
            var = True
        elif self.log_level == u'debug':
            var = True
        return var
