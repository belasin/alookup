#!/usr/bin/env bash
set -e
export C_FORCE_ROOT="true"

cp /usr/share/zoneinfo/Africa/Johannesburg /etc/localtime && echo "Africa/Johannesburg" >  /etc/timezone

if [ ! -f /alookup/configs/config.ini ]; then
    cp /alookup/config.ini /alookup/configs/config.ini
fi

if [ "$1" = 'shell' ]; then
    exec pshell /alookup/configs/config.ini
fi

if [ "$1" = 'serve' ]; then
    exec pserve /alookup/configs/config.ini
fi

exec "$@"