#!/bin/bash

rm -r ./other_files/tmux-resurrect
cp -r ~/.config/tmux-resurrect ./other_files/tmux-resurrect
rm -r ./other_files/tmux-continuum
cp -r ~/.config/tmux-continuum ./other_files/tmux-continuum
rm -r ./other_files/ranger
cp -r ~/.config/ranger ./other_files/ranger
cp ~/.tmux.conf ./other_files/.tmux.conf
rm -r ./other_files/.vim
cp -r ~/.vim ./other_files/.vim
cp ~/.vimrc ./other_files/.vimrc
cp ~/.config/flake8 ./other_files/flake8
cp ~/.bashrc ./other_files/.bashrc

# for controller only
awk '/###_controller_bash_cmd_only_START/{flag=1;next}/###_controller_bash_cmd_only_STOP/{flag=0}flag' ~/.bashrc >> ./other_files/append_rc
