# -*- coding: utf-8 -*-

import datetime, logging, os, random
import requests
from ezb_queue_control import common
# from ezb_queue_control.config import settings


def setup_file_logger( file_log_dir, file_log_level ):
    """ Returns a logger to write to a file. """
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
    """ Returns a db_logger_instance that'll post json to a db-logger webservice. """
    db_logger = DB_Logger( settings.DB_LOGGER_URL, settings.DB_LOGGER_USERNAME, settings.DB_LOGGER_PASSWORD )
    return db_logger


class DB_Logger(object):
    """ Sends json to proxy-service that updates a db logging parts of easyborrow processing. """

    def __init__( self, url, username, password, log_level, file_logger=None ):
        """ Holds state; user/pass for http-basic-auth. """
        self.url = url
        self.username = username
        self.password = password
        self.log_level = log_level
        self.file_logger = file_logger

    def update_log( self, message, message_importance ):
        if _worthwhile_check( message_importance ) == False:
            return
        payload = { u'message': message }
        r = requests.post( self.url, data=json.dumps(payload), auth=(self.username, self.password) )
        print '- status_code, %s' % r.status_code
        return

    def worthwhile_check( self, message_importance ):
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
