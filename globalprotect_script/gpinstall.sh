#!/bin/bash
#
## Purpose - Global Protect For Linux Installation Script
## Version - 1.9
## Author - Swapnil S. Hendre
## Created On - 09/16/2018
## Updated On - 01/10/2019
## Updated On - 05/08/2019
## Updated On - 05/20/2019
#
#

GPU_OS_Check ()
{
	echo "Pre-Installation-Check: Operating System"
        grep Ubuntu /proc/version 2>&1 > /dev/null
        os_ubuntu=$?
        grep Red /proc/version 2>&1 > /dev/null
        os_centos=$?
        if [ $os_ubuntu -eq 0 ]; then
		retval="Ubuntu"
        elif [ $os_centos = 0 ] ; then
		retval="CentOS"
        else
		retval="Unknown"
        fi
}


GPU_SUDO_Check ()
{
echo "Pre-Installation-Check : Checking SUDO Access For User"
/usr/bin/sudo su -c "tail -1 /etc/shadow" > /dev/null 2>&1
if [ $? != 0 ]; then
	echo
        echo -e '\033[1mPre-Installation-Check Failed:User does not have sudo root permissions,Please grant user sudo root permissions\033[0m'
	echo 
        exit 1
fi
}

GPU_Space_Check ()
{
echo "Pre-Installation-Check: Storage"
df_var_tmp=$(df /var/tmp --output=avail  | awk 'FNR == 2 {print}')
df_opt=$(df /opt --output=avail  | awk 'FNR == 2 {print}')

if [ $df_var_tmp -lt 25000 ] || [ $df_opt -lt 25000 ];then
        echo "Not Enough Space: Minimum Space Requirements For /var/tmp and /opt 25 MB"
        exit 1
fi
}

GPU_EUID_Check ()
{
echo "Pre-Installation-Check: User-ID"
if [ $EUID = 0 ]; then
        echo -e '\033[1m	Pre-Installation-Check Failed: You are logged in as Super User (root), Please login as non Super User (root) Account\033[0m'
    echo
    exit
fi
}

GPU_Network_Check ()
{
mkdir -p /var/tmp/GP-Linux/logs
ping -c2 -W2 -q ssend.vmware.com >> /var/tmp/GP-Linux/logs/globalprotect.log.$orgdate
if [ $? != 0 ]
then
        echo -e '\033[1m	Pre-Installation-Check Failed: Please Check Network Connectivity\033[0m'
exit
fi
}

GPU_Banner_2 ()
{
/usr/bin/clear
echo "                  ##########################################"
echo "                    Global Protect For Linux Installation"
echo "                  ##########################################"
echo
echo -e '\033[1mPre-Installation-Checks Successful:Starting Installation....\033[0m'
echo
echo
}

GPU_Ubuntu_Install ()
{
cd /var/tmp/GPL419
/usr/bin/sudo dpkg -i ./GlobalProtect_deb-4.1.9.0-2.deb
echo
echo -e '\033[1mInstallation has been completed:Connect to GlobalProtect GW using command gpu -c \033[0m'
}

GPU_CentOS_Install ()
{
cd /var/tmp/GPL419
/usr/bin/sudo yum localinstall -y ./GlobalProtect_rpm-4.1.9.0-2.rpm 
echo
echo -e '\033[1mInstallation has been completed:Connect to GlobalProtect GW using command gpu -c\033[0m'
}

GPU_Download ()
{
mkdir -p /var/tmp/GPL419
cd /var/tmp/GPL419
wget -q --no-check-certificate 'https://ftpsite.vmware.com/download?domain=FTPSITE&id=cec15c0f3bc941d1a9adef6178fae226-566ec7a187db4140a3f4c26087f65172' -O PanGPLinux-4.1.9-c3.tgz
tar -xf PanGPLinux-4.1.9-c3.tgz
wget -q --no-check-certificate 'https://ftpsite.vmware.com/download?domain=FTPSITE&id=c2858413564c47a48d16dc6cf2309d2c-714aed2cc88244bb8c9e524620beba6b' -O /var/tmp/GP-Linux/gpu
/usr/bin/sudo /bin/cp -p /var/tmp/GP-Linux/gpu /usr/bin/gpu
/bin/chmod 755 /usr/bin/gpu
/usr/bin/sudo /bin/rm -f /var/tmp/GP-Linux/gpu
}

GPU_Banner ()
{
/usr/bin/clear
echo "                  ##########################################"
echo "                    Global Protect For Linux Installation"
echo "                  ##########################################"
echo
echo "		   Pre-Requisites:"
echo "		   1. Space > 25 MB in /opt and /var/tmp"
echo "		   2. Supported OS - Ubuntu and CentOS"
echo "		   3. Must be logged in as non-super user"
echo "		   4. non-super user much have sudo root permissions"
echo
echo
}
#
##
#
orgdate=`/bin/date +%F`
mkdir -p /var/tmp/GPL419
GPU_OS_Check
case $retval in
	Ubuntu )
	GPU_Banner
	GPU_SUDO_Check
	GPU_EUID_Check
	GPU_Space_Check
	GPU_Network_Check
	/usr/bin/clear
	GPU_Banner_2
	GPU_Download
	GPU_Ubuntu_Install
	exit 0
	;;
	CentOS )
	GPU_Banner
	GPU_SUDO_Check
	GPU_EUID_Check
	GPU_Space_Check
	GPU_Network_Check
	/usr/bin/clear
	GPU_Banner_2
	GPU_Download
	GPU_CentOS_Install
	exit 0
	;;
	* )
	echo "Unsupport OS"
	exit 1
	;;
esac
