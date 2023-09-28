# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples
# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac


# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

##############################################################################################

. /mnt/builds/pr-builder/bash_sources/.bashrc-container

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

alias gpull='git pull --rebase'
alias gpush='git push'
alias gstat='git status'
alias glsstash='git stash list'
alias gllstash='git stash show'
alias gstash='git stash'
alias gpop='git stash pop'
alias glog='git log --no-merges'


if [ -f /mnt/builds/pr-builder/bash_sources/.bashrc-container ]; then
    . /mnt/builds/pr-builder/bash_sources/.bashrc-container
fi

BLR_BASE="10.102.64.0"
BLR_NET_MASK="255.255.252.0"

function pythonpath {
    ws=`git rev-parse --show-toplevel`
    export PYTHONPATH=$ws/build/python:$ws/python/bin:$ws/python/lib:$ws/test/robot/new/lib:$ws/test/avitest:$ws/thirdparty/ftw
}

function mydistmake {
    lts_version=`lsb_release -rs`
    # Host machines ip from where the containerized build run
    my_ip=$HOST

    IFS=. read -r i1 i2 i3 i4 <<< $my_ip
    IFS=. read -r m1 m2 m3 m4 <<< $BLR_NET_MASK
    my_ip_mask=$(printf "%d.%d.%d.%d\n" "$((i1 & m1))" "$((i2 & m2))" "$((i3 & m3))" "$((i4 & m4))")

    if [ $my_ip_mask = $BLR_BASE ]; then
        export DISTCC_HOSTS=`cat /mnt/files/khaltore/distcc-hosts-BLR-$lts_version | (echo "--localslots=8" && cat)`
    else
        export DISTCC_HOSTS=`cat /mnt/files/khaltore/distcc-hosts-$lts_version`
    fi
    CC='distcc gcc' CXX='distcc g++' make -j$(distcc -j)
}

function distcmake {
    local args=( "$@" )
    CC='distcc gcc' CXX='distcc g++' cmake ${args[@]} ..
}

function nodistcmake {
    CC='gcc' CXX='g++' cmake ..
}


function nodistmake {
    export DISTCC_HOSTS='localhost'
    make -j$(distcc -j) && make install_avi
}

function gitdelbr {
    git branch -D $@
    git push --delete origin $@
}


# Enable tab completion
# source ~/.config/git-completion.bash

# colors!
green="\[\033[0;32m\]"
blue="\[\033[0;34m\]"
purple="\[\033[0m\]"
reset="\[\033[0m\]"

# Change command prompt
source ~/.config/git-prompt.sh
export GIT_PS1_SHOWDIRTYSTATE=1
export GIT_PS1_SHOWSTASHSTATE=2
export GIT_PS1_SHOWUNTRACKEDFILES=3
# '\u' adds the name of the current user to the prompt
# '\$(__git_ps1)' adds git-related stuff
# '\W' adds the name of the current directory
export PS1="$purple\u$green\$(__git_ps1)$blue:[\`pwd\`]\n $ $reset"

export EDITOR='vim'
export VISUAL='vim'
export PYTHONHTTPSVERIFY=0

# After each command, save and reload history
export PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"

alias ranger='ranger --choosedir=$HOME/.rangerdir; LASTDIR=`cat $HOME/.rangerdir`; cd "$LASTDIR"'

function ws {
        loc=`git rev-parse --show-toplevel`
            cd $loc
        }

export -f ws
export PYTHONPATH=/home/aviuser/workspace/avi-dev/python/lib:/home/aviuser/workspace/avi-dev/python/bin:/home/aviuser/workspace/avi-dev/test/avitest:/home/aviuser/workspace/avi-dev/test/robot/new/lib:/home/aviuser/workspace/avi-dev/thirdparty/ftw:/home/aviuser/workspace/avi-dev/build/python:/home/aviuser/workspace/avi-dev/test/ansible/lib
export LD_LIBRARY_PATH=/home/aviuser/workspace/avi-dev/build/lib

export GOPATH=$HOME/workspace/avi-dev/go:$HOME/go

alias wsp=ws
alias r=ranger
alias vsphere_ips='python3 /home/aviuser/automation_stuff/vsphere_ips/get_empty_ips_vsphere-vmware.py'
alias vimx='vim -X'
alias sgpt='sgpt --no-animation'

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=200000
HISTFILESIZE=500000

########################################################


. $HOME/containerized-testenv/bash_sources/.bashrc-container

export PATH="$PATH:/home/aviuser/bin"
