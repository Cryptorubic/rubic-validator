#! /bin/bash

exec celery --app backend beat --loglevel=DEBUG -S django
