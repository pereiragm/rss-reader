#!/bin/bash

if [ $PROCESS_TYPE = "web" ]; then
  echo "Starting web application..."
  uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 80
  elif [ $PROCESS_TYPE = "worker" ]; then
    echo "Starting worker process..."
    celery -A app.worker worker -l INFO
  elif [ $PROCESS_TYPE = "beat" ]; then
    echo "Starting beat process..."
    celery -A app.worker beat -l INFO
  else
    echo "The env var PROCESS_TYPE must be one of: web, worker, beat."
fi
