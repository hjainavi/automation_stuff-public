#!/bin/bash
# make sure chmod +x avipdbportal.sh
# args "start" to start a single threaded and single process django portal with access to pdb in line
# args "change" to change the configs so that above run comand is possible
# args "changeback" to change the configs as factory-default for django server
# args "reload" gracefully restarts the uwsgi process
# args "stop" will gracefully kill the uwsgi process
# args "kill" will instantly kill the process

export PYTHONPATH=/opt/avi/python/lib:/opt/avi/python/bin/portal:/usr/local/lib/python3.8/dist-packages:/usr/local/lib/python3.8/site-packages:$PWD/avipdb
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=2

ipdb_str = $(pip3 list | grep ipdb)
if [[ "ipdb" == *"$ipdb_str"* ]]; then
    echo "ipdb installed"
else
    pip3 install ipdb
fi

chmod +x ./change-conf.py

if [ -z "$3" ];then
    export AVI_PDB_KEY='-1'
else
    export AVI_PDB_KEY=$3
fi

if [ "$1" = "start" ];then
    if [ "$2" = "pdb" ];then
        export AVI_PDB_FLAG="pdb"
    elif [ "$2" = "ipdb" ];then
        export AVI_PDB_FLAG="ipdb"
    else
        export AVI_PDB_FLAG="none"
    fi
    exec uwsgi --stats 127.0.0.1:5048 --stats-http --honour-stdin --ini ./pdb-portal.ini:portal
    #./test.py
elif [ "$1" = "change" ];then
    ./change-conf.py $1 aviportal.service
    systemd-analyze verify /etc/systemd/system/aviportal.service
    if [ $? -eq 0 ]; then
        systemctl daemon-reload
        service aviportal stop
        sleep 5
        service aviportal stop
        echo $(service aviportal status | tail -4)
    else
        echo FAIL
    fi

elif [ "$1" = "changeback" ];then
    ./change-conf.py $1 aviportal.service
    systemd-analyze verify /etc/systemd/system/aviportal.service
    if [ $? -eq 0 ]; then
        systemctl daemon-reload
        service aviportal stop
        service aviportal start
        sleep 2
        echo $(service aviportal status | tail -8)

    else
        echo FAIL
    fi
else
    echo 'INVALID ARGS'
fi
