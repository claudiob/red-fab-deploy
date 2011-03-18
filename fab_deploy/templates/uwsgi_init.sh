#!/bin/sh

### BEGIN INIT INFO
# Provides:          uwsgi
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the uwsgi app server
# Description:       starts uwsgi app server using start-stop-daemon
### END INIT INFO

# From http://library.linode.com/web-servers/nginx/python-uwsgi/reference/init-deb.sh

PATH=/opt/uwsgi:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/uwsgi

OWNER=root #uwsgi chowns itself

NAME=uwsgi
DESC=uwsgi

test -x $DAEMON || exit 0

# Include uwsgi defaults if available
if [ -f /etc/default/uwsgi ] ; then
        . /etc/default/uwsgi
fi

set -e

DAEMON_OPTS="--ini /etc/uwsgi/uwsgi.ini"

case "$1" in
  start)
        echo -n "Starting $DESC: "
        start-stop-daemon --start --chuid $OWNER:$OWNER --user $OWNER \
                --exec $DAEMON -- $DAEMON_OPTS
        echo "Done."
        ;;
  stop)
        echo -n "Stopping $DESC: "
        start-stop-daemon --signal 3 --quiet --retry 2 --stop \
                --exec $DAEMON
        echo "Done."
        ;;
  reload)
        killall -1 $DAEMON
        ;;
  force-reload)
        killall -15 $DAEMON
       ;;
  restart)
        echo -n "Restarting $DESC: "
        start-stop-daemon --signal 3 --quiet --retry 2 --stop \
                --exec $DAEMON
        sleep 1
        start-stop-daemon --user $OWNER --start --quiet --chuid $OWNER:$OWNER \
               --exec $DAEMON -- $DAEMON_OPTS
        echo "Done."
        ;;
  status)  
        killall -10 $DAEMON
        ;;
      *)  
            N=/etc/init.d/$NAME
            echo "Usage: $N {start|stop|restart|reload|force-reload|status}" >&2
            exit 1
            ;;
    esac
    exit 0