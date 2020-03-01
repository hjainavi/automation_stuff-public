#!/bin/bash

# exit when any command fails
set -e
set -x
# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT
sudo apt-get update


if [ -d "/opt/avi/python" ]
then
    echo "a controller vm"
    if grep -wq "avishell" ~/.bashrc
    then
        :
    else
        cat  ./other_files/append_rc >> ~/.bashrc
        cat  ./other_bashrc_cust >> ~/.bashrc
        cat  ./other_files/ctlr_hist.txt >> ~/.bash_history
    fi
else
    echo "not a controller vm"
    cp -v ./other_files/.bashrc ~/.bashrc
fi

# transfer git branch command prompt customizations to .config
if [ ! -d "$HOME/.config" ];then
    mkdir ~/.config
fi
#echo "nameserver 8.8.8.8" >> /etc/resolv.conf
cp -v ./git_show_branch_cmd/git-completion.bash ~/.config/git-completion.bash
cp -v ./git_show_branch_cmd/git-prompt.sh ~/.config/git-prompt.sh

#if grep -q "source ~/.config/git-completion.bash" "$HOME/.bashrc"; then
#    echo "already changed bashrc"
#else
#    cat ./git_show_branch_cmd/bash_profile_course >> ~/.bashrc
#fi

echo "==================git config and bashrc done"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get install software-properties-common python-software-properties -y
sudo add-apt-repository ppa:git-core/ppa -y;add-apt-repository ppa:keithw/mosh -y;add-apt-repository ppa:pi-rho/dev -y
echo "==================add-apt done"

sudo apt-get update;apt-get install vim-gnome aria2 python-ipdb ranger git xauth xclip mosh -y
sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install tmux

echo "==================apt-get done"

sudo pip install flake8
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


cp -r ./other_files/tmux-resurrect ~/.config/tmux-resurrect
cp -r ./other_files/tmux-continuum ~/.config/tmux-continuum
cp -r ./other_files/ranger ~/.config/ranger
cp ./other_files/.tmux.conf ~/.tmux.conf
cp -r ./other_files/.vim ~/.vim
cp ./other_files/flake8 ~/.config/flake8
cp ./other_files/.vimrc ~/.vimrc
cp ./other_files/import.py ~/import.py
cp ./other_files/pool.py ~/pool.py
cp ./other_files/cluster.py ~/cluster.py
cp ./other_files/import1.py ~/import1.py

echo "==================other_files done"

vim +PluginInstall +qall
echo "===================vim plugininstall done"

sed -i 's/X11Forwarding no/X11Forwarding yes/g' /etc/ssh/sshd_config
service ssh restart
echo "==================X11 done"

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
    git init
    git add -A
    git commit -m "first commit"
    flake8 --install-hook git
    echo "===================git init done /opt/avi/python"
else
    echo "Not a controller VM setting up git config"
    # run python script to install hook to run flake8 --install-hook git in repo
    ./install-hook.py
    git config --global user.email "harshjain@avinetworks.com"
    git config --global user.name "harsh jain"
    echo "setting git global config user.email harshjain@avinetworks.com"
fi


