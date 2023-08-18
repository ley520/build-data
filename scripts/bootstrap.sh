#!/bin/bash
cd "$(dirname "$0")"
pwd
cd ..
# 启动 Celery worker 进程
celery -A buildDataBackend worker -l info --logfile="../log/celery.log" --pidfile=./celery.pid &

# 等待 worker 进程启动完成后，再启动 beat 进程
while true; do
  sleep 1
  celery -A buildDataBackend inspect ping >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    break
  fi
done
celery -A buildDataBackend beat --pidfile=./celery_beat.pid &

# 等待 beat 进程启动完成后，再启动 flower 进程
while true; do
  sleep 1
  celery -A buildDataBackend inspect ping >/dev/null 2>&1
  celery -A buildDataBackend status >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    break
  fi
done
celery -A buildDataBackend flower --pidfile=./flower.pid &
