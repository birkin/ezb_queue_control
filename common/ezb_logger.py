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

    def __init__( self, url, username, password ):
        self.url = url
        self.username = username
        self.password = password

    def update_log( self, message, message_importance=u'low' ):
        return


# class DB_Logger(object):
#   """ Manages databaselogging.
#       All database log entries, as well as failure attempts, also populate a file-log.
#       self.session_identifier is populated early, and logger instance is passed to other classes. """

#   def __init__( self, log_url=None, log_key=None, logentry_minimum_importance_level=None, session_identifier=None, file_logger=None ):
#     """ Sets up basics. """
#     self.file_logger = file_logger
#     self.log_url = log_url if( log_url ) else dev_settings.DB_LOG_URL
#     self.log_key = log_key if( log_key ) else dev_settings.DB_LOG_KEY
#     self.logentry_minimum_importance_level = logentry_minimum_importance_level if( logentry_minimum_importance_level ) else dev_settings.DB_LOGENTRY_MINIMUM_IMPORTANCE_LEVEL
#     self.session_identifier = session_identifier if( session_identifier ) else u'temp--%s--%s' % ( datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), random.randint(1000,9999) )  # used until request-number is obtained

#   def update_log( self, message, message_importance=u'low' ):
#     """ Updates database log, or file log on exception. """
#     try:
#       if self.file_logger:
#         self.file_logger.info( u'message_importance is: %s' % message_importance )
#       assert message_importance in [u'low', u'high'], u'BAD MESSAGE IMPORTANCE'
#       update_log_flag = False
#       if message_importance == u'high':
#         update_log_flag = True
#       elif ( message_importance == u'low' and self.logentry_minimum_importance_level == u'low' ):
#         update_log_flag = True
#       if update_log_flag:
#         values = { u'message': message, u'identifier': self.session_identifier, u'key': self.log_key }
#         r = requests.post( self.log_url, data=values, verify=False )
#       # print u'- in ezb_logger.DB_Logger.update_log(); update_log returning.'
#       return
#     except:
#       message = u'- in dev_code.ezb_logger.py; DB_Logger().update_log(); error detail: %s' % make_error_string()
#       # print message
#       if self.file_logger:
#         self.file_logger.info( u'session, %s; message, %s' % (self.session_identifier, message) )
#       return
