#!/bin/bash

NAME=grakon_new


PIDFILE=/var/run/$NAME.pid
SOCKET=/home/serg/sites/$NAME.sock
DIR=/home/serg/sites/$NAME/
ENV=/home/serg/env/$NAME/bin/activate

METHOD="threaded" # "prefork"

action=${1:-restart}

start() {
    cd ${DIR}
    source ${ENV}
    python manage.py runfcgi method=${METHOD} socket=${SOCKET} pidfile=${PIDFILE} && echo "fcgi started."
    chown nginx:nginx ${SOCKET}
}

stop() {
    if [ -e ${PIDFILE} ]
    then
        kill `cat ${PIDFILE}` && rm -f ${PIDFILE} &&  echo "fcgi stoped."
    fi
}

restart() {
    stop
    start
}

usage() {
echo "Arguments should be: start, stop, restart or None."
}

case ${action} in
    start   ) start   ;;
    stop    ) stop    ;;
    restart ) restart ;;
    *       ) usage   ;;
esac
