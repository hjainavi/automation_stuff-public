#!/bin/bash

chmod +x ./_go-binary.py

if [ "$1" = "change" ]; then
    if [ "$2" = "apiserver" ];then
        ./_go-binary.py change apiserver
        mv /home/admin/go-controller /opt/avi/bin/go-controller-new && systemctl restart apiserver.service
    fi

    if [ "$1" = "octavius" ];then
        ./_go-binary.py change octavius
        mv /home/admin/go-controller /opt/avi/bin/go-controller-new && systemctl restart octavius.service
    fi
fi

if [ "$1" = "changeback" ]; then
    ./_go-binary.py changeback apiserver
    systemctl restart apiserver.service
    ./_go-binary.py changeback octavius
    systemctl restart octavius.service
fi