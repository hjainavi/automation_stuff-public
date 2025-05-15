#!/bin/bash

chmod +x ./_go-binary.py

if [ "$1" = "change" ]; then
    if [ -f "/home/admin/go-controller" ]; then
        echo "/home/admin/go-controller file exists."
        mv /home/admin/go-controller /opt/avi/bin/go-controller-new
    else
        echo "/home/admin/go-controller file does not exist."
        if [ -z "/opt/avi/bin/go-controller-new" ]; then
            echo "Error : /opt/avi/bin/go-controller-new file does not exist."
            return 1
        fi
    fi
    if [ "$2" = "apiserver" ];then
        ./_go-binary.py change apiserver
        systemctl restart apiserver.service
    fi

    if [ "$2" = "octavius" ];then
        ./_go-binary.py change octavius
        systemctl restart octavius.service
    fi
fi

if [ "$1" = "changeback" ]; then
    ./_go-binary.py changeback apiserver
    ./_go-binary.py changeback octavius
    systemctl restart apiserver.service ; systemctl restart octavius.service
fi