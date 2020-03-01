#!/bin/bash
# args controller_ip , user , password
if [ -z "$1" ];then
    echo "Controller IP ?"
    read ctlr_ip
fi
ctlr_ip=$1
if [ -z "$2" ];then
    echo "Controller username ?"
    read username
fi
username=$2
if [ -z "$3" ];then
    echo "Controller password ?"
    read password
fi
password=$3
#sudo ./prepare_controller_customizations.sh
#echo "creating a tar file from controller_customization folder"
#tar -cf ../ctlr_custom.tar.gz ../controller_customization
#echo "transfering ctlr_custom.tar.gz to controller"
#SSHPASS=$password sshpass -e scp -o StrictHostKeyChecking=no ../ctlr_custom.tar.gz $username@$ctlr_ip:~/

echo "extracting on ctlr"
SSHPASS=$password sshpass -e ssh -o StrictHostKeyChecking=no $username@$ctlr_ip 'ifconfig; exit'

