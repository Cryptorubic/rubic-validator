#! /bin/bash

exec celery --app backend worker --loglevel=DEBUG -E --logfile=celery.log
