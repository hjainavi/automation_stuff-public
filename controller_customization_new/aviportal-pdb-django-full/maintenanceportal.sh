#!/bin/bash
# make sure chmod +x avipdbportal.sh
# args "start" to start a single threaded and single process django portal with access to pdb in line
# args "change" to change the configs so that above run comand is possible
# args "changeback" to change the configs as factory-default for django server
# args "reload" gracefully restarts the uwsgi process
# args "stop" will gracefully kill the uwsgi process
# args "kill" will instantly kill the process

PHOTON_CTLR=false
UBUNTU_CTLR=false
if lsb_release -d | grep -q 'Photon'; then
    PHOTON_CTLR=true
    echo "Photon Ctlr"
    echo "Exiting"
    exit 1
fi
if lsb_release -d | grep -q 'Ubuntu'; then
    UBUNTU_CTLR=true
    echo "Ubuntu Ctlr"
fi


export PYTHONPATH=/opt/avi/python/lib:/opt/avi/python/bin/portal:/usr/local/lib/python2.7/dist-packages:$PWD/avipdb
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION=2

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
    exec uwsgi --honour-stdin --ini ./pdb-portal.ini:maintenanceportal
    #./test.py
elif [ "$1" = "change" ];then
    ./change-conf.py $1 maintenanceportal.service
    systemd-analyze verify /etc/systemd/system/maintenanceportal.service
    if [ $? -eq 0 ]; then
        systemctl daemon-reload
        service maintenanceportal stop
        sleep 5
        service maintenanceportal stop
        echo $(service maintenanceportal status | tail -4)
    else
        echo FAIL
    fi

elif [ "$1" = "changeback" ];then
    ./change-conf.py $1 maintenanceportal.service
    systemd-analyze verify /etc/systemd/system/maintenanceportal.service
    if [ $? -eq 0 ]; then
        systemctl daemon-reload
        service maintenanceportal stop
        service maintenanceportal start
        sleep 2
        echo $(service maintenanceportal status | tail -8)
    else
        echo FAIL
    fi
else
    echo 'INVALID ARGS'
fi
