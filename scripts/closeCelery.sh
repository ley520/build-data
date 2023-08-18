#!/bin/bash
cd "$(dirname "$0")"
pwd
cd ..

celery_pid_path='celery.pid'
celery_beat_pid_path='celery_beat.pid'
kill -TERM `cat celery.pid`
kill -TERM `cat celery_beat.pid`
ps -ef | grep flower | grep -v grep | awk '{print $2}' | xargs kill -9

if [ -f "$celery_pid_path" ]; then # 判断文件是否存在
  rm "$celery_pid_path"
  echo "${celery_pid_path}已删除"
else
  echo "${celery_pid_path}不存在，无法删除"
fi
if [ -f "$celery_beat_pid_path" ]; then # 判断文件是否存在
  rm "$celery_beat_pid_path"
  echo "${celery_beat_pid_path}已删除"
else
  echo "${celery_beat_pid_path}不存在，无法删除"
fi
