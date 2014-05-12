#!/bin/bash

# NOTE: Assumes rq worker(s) started from ezborrow_python_code directory.

WORKER_NAME=ezb_worker_$RANDOM
LOG_FILENAME=$ezb_ctl__WORKER_LOG_DIR/$WORKER_NAME.log

echo "worker name: " $WORKER_NAME
echo "log filename: " $LOG_FILENAME
echo "queue name: " $ezb_ctl__QUEUE_NAME

# rqworker --name $WORKER_NAME $QUEUE_NAME >> $LOG_FILENAME 2>&1 &
rqworker --name $WORKER_NAME $ezb_ctl__QUEUE_NAME
