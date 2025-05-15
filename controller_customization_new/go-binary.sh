#!/bin/bash

chmod +x ./_go-binary.py

if [ "$1" = "change" ]; then
    mv /home/admin/go-controller /opt/avi/bin/go-controller-new
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