#!/bin/bash

# exit when any command fails
set -e
set -x
# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT


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


#release=$(lsb_release -a 2>&1)
#if [[ $release == *"focal"* ]]

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

./controller_cust_install_only.sh

