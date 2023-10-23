#!/bin/bash

# exit when any command fails
set -e
set -x
# keep track of the last executed command
#trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

DEV_VM=false
PHOTON_CTLR=false
UBUNTU_CTLR=false

if [ -d "/opt/avi/python" ] ; then
    if ! whoami | grep -q 'root'; then
        echo "User is not root"
        exit 1
    fi
    if lsb_release -d | grep -q 'Photon'; then
        PHOTON_CTLR=true
    fi
    if lsb_release -d | grep -q 'Ubuntu'; then
        UBUNTU_CTLR=true
    fi
else
    DEV_VM=true
fi


#release=$(lsb_release -a 2>&1)
#if [[ $release == *"focal"* ]]
if $PHOTON_CTLR ; then
    tdnf -y -q install tmux git
    pip -q install ranger-fm flake8 ipdb
    cp ./other_files/aria2c /usr/bin/
    chmod o+x /usr/bin/aria2c
    cp ./other_files/mosh-server /usr/bin/
    chmod o+x /usr/bin/mosh-server
    ./other_files/tmux_start_script.sh
    iptables -A INPUT -p udp -m multiport --dports 60000:60100 -j ACCEPT
    iptables -A INPUT -p tcp --dport 2345 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
    iptables-save > /etc/systemd/scripts/ip4save


elif $UBUNTU_CTLR ; then
    echo "==================git config and bashrc done"
    export DEBIAN_FRONTEND=noninteractive

    sudo apt-get -q update;apt-get install aria2 ranger git mosh -y -q
    sudo DEBIAN_FRONTEND=noninteractive apt-get -y -q install tmux

    echo "==================apt-get done"
    pip3 -q install flake8
    pip3 -q install ipdb
    ./other_files/tmux_start_script.sh
fi
    


echo "===============pip install flake8"
git config --global --bool http.sslVerify false
git config --global push.default current
git config --global credential.helper "cache --timeout=3600"
git config --global core.editor vim
git config --global --bool core.autocrlf false
git config --global --bool flake8.strict true
echo "===============git config flake8.strict true"

#if grep -q "alias ranger" "$HOME/.bashrc"; then
#    echo "already changed other bashrc"
#else
#    cat ./other_bashrc_cust >> ~/.bashrc
#fi

vim +PluginInstall +qall
echo "===================vim plugininstall done"

#sed -i 's/X11Forwarding no/X11Forwarding yes/g' /etc/ssh/sshd_config
#service ssh restart
#echo "==================X11 done"

if [ -d "/opt/avi/python" ];
then
    echo "creating a git repository of /opt/avi/python"
cat >/opt/avi/python/.gitignore <<EOL
*.pyo
*.pyc
*.swo
*.swp
EOL

    cd /opt/avi/python
    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"
    git config --global pull.rebase false
    git config --global --add safe.directory '*'
    git init
    git add -A > /dev/null 2>&1
    git commit -m "first commit" > /dev/null 2>&1
    # flake8 --install-hook git
    echo "===================git init done /opt/avi/python"
else
    echo "Not a controller VM setting up git config"
    # run python script to install hook to run flake8 --install-hook git in repo
    #./install-hook.py
    git config --global user.email "harshj@vmware.com"
    git config --global user.name "harsh jain"
    git config --global pull.rebase false
    echo "setting git global config user.email harshj@vmware.com"
fi


