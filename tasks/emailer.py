# -*- coding: utf-8 -*-

""" Handles emailing.
    Note: admittedly odd to require django just for emailing, but it
          takes care of all unicode issues and is just so easy. """

# from django.core import mail

# from django.core.mail.backends.smtp import EmailBackend
# bknd = EmailBackend( host='localhost', port=25, username='', password='', use_tls=False )

# from django.core.mail.backends.console import EmailBackend
# bknd = EmailBackend( encoding='utf-8' )


# email = mail.EmailMessage(
#     subject='test',
#     body='Body goes here',
#     from_email='from@example.com',
#     to=['to1@example.com', 'to2@example.com'],
#     bcc=['bcc@example.com'],
#     headers = {'Reply-To': 'another@example.com'},
#     connection = bknd,
#     )
# email.send()


# import smtplib
# import email.utils
# from email.mime.text import MIMEText

# # Create the message
# msg = MIMEText( u'This is the body of the méssage.'.encode(u'utf-8', u'replace') )
# msg[u'To'.encode(u'utf-8', u'replace')] = email.utils.formataddr( (u'Recipiént'.encode(u'utf-8', u'replace'), u'recipiént@example.com'.encode(u'utf-8', u'replace')) )
# msg[u'From'.encode(u'utf-8', u'replace')] = email.utils.formataddr( (u'Authór'.encode(u'utf-8', u'replace'), u'authór@example.com'.encode(u'utf-8', u'replace')) )
# msg[u'Subject'.encode(u'utf-8', u'replace')] = u'Sîmple test message'.encode(u'utf-8', u'replace')

# # server = smtplib.SMTP('mail')
# server = smtplib.SMTP( u'localhost:1025'.encode(u'utf-8', u'replace') )
# server.set_debuglevel(True) # show communication with the server
# try:
#     server.sendmail('author@example.com', ['recipient@example.com'], msg.as_string())
# finally:
#     server.quit()


# import smtplib
# import email.utils
# from email.mime.text import MIMEText

# # Create the message
# msg = MIMEText('This is the body of the message.')
# msg['To'] = email.utils.formataddr(('Recipient', 'recipient@example.com'))
# msg['From'] = email.utils.formataddr(('Author', 'author@example.com'))
# msg['Subject'] = 'Simple test message'

# # server = smtplib.SMTP('mail')
# server = smtplib.SMTP('localhost:1025')
# server.set_debuglevel(True) # show communication with the server
# try:
#     server.sendmail('author@example.com', ['recipient@example.com'], msg.as_string())
# finally:
#     server.quit()


import smtplib
import email.utils
from email.mime.text import MIMEText

# Create the message
msg = MIMEText('This is the body of the message.')
msg['To'] = '%s, %s' % ( email.utils.formataddr(('Recipient1', 'recipient1@example.com')), email.utils.formataddr(('Recipient2', 'recipient2@example.com')) )
msg['From'] = email.utils.formataddr(('Author', 'author@example.com'))
msg['Subject'] = 'Simple test message'

# server = smtplib.SMTP('mail')
server = smtplib.SMTP('localhost:1025')
server.set_debuglevel(True) # show communication with the server
try:
    server.sendmail('author@example.com', ['recipient1@example.com', 'recipient2@example.com'], msg.as_string())
finally:
    server.quit()


# def email_illiad_error( data ):
#     """ Emails illiad info. """
#     print u'emailer code will go here'
#     return


def email_illiad_error( data ):
    """ Emails illiad info. """
    email = mail.EmailMessage(
        subject='Hello',
        body='Body goes here',
        from_email='from@example.com',
        to=['to1@example.com', 'to2@example.com'],
        bcc=['bcc@example.com'],
        headers = {'Reply-To': 'another@example.com'},
        connection = mail.get_connection( backend='django.core.mail.backends.smtp.EmailBackend' ),
        )
    email.send()
    return


