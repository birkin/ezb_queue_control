# -*- coding: utf-8 -*-

""" Clear out target job queue.
    Useful for experimenting with rq & redis, starting queue from scratch.
    """

import os, pprint, sys
import redis


rds = redis.Redis( u'localhost' )
TARGET_QUEUE = unicode( os.environ.get(u'ezb_ctl__QUEUE_NAME') )
print u'- target-queue is: %s' % TARGET_QUEUE; print u'--'
FULL_QUEUE_NAME = u'rq:queue:%s' % TARGET_QUEUE
print u'- full-queue-name is: %s' % FULL_QUEUE_NAME; print u'--'


# check whether queue exists
if rds.type( FULL_QUEUE_NAME ) == u'none':
  print u'- queue `%s` does not exist' % FULL_QUEUE_NAME; print u'--'
  sys.exit()

# get members
assert rds.type( FULL_QUEUE_NAME ) == u'list'
print u'- length of target-queue starts at: %s' % rds.llen( FULL_QUEUE_NAME )
members = rds.lrange( FULL_QUEUE_NAME, 0, -1 )
print u'- target-queue members...'; pprint.pprint( members ); print u'--'

# inspect jobs
for entry in members:
  assert type(entry) == str
  print u'- entry is: %s' % unicode( entry )
  job_id = u'rq:job:%s' % unicode( entry )
  print u'- job_id is: %s' % job_id

  # ensure target-queue-job really exists
  if rds.type( job_id ) == u'none':  # job was already deleted (i.e. interactive redis-cli experimentation), so remove it from target-queue-list
    print u'- job_id  was not found; entry still removed from queue'
  else:
    # remove the job
    rds.delete( job_id )
    print u'- job id removed'

  # remove the queue's reference
  rds.lrem( FULL_QUEUE_NAME, entry, num=0 )  # note count and value-name are reversed from redis-cli syntax... (redis-cli) > lrem "rq:queue:NAME" 0 "06d0a46e-21ec-4fd3-92f8-f941f32101c4"
  print u'- job reference removed from queue'

  print u'- length of target-queue is now: %s' % rds.llen( FULL_QUEUE_NAME ); print u'--'

# end
