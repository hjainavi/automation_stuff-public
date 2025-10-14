TMUX_SESSION_NAME='harsh'
tmux new-session -d -s $TMUX_SESSION_NAME >/dev/null
if [ -f "/var/log/upstart/aviportal.log" ]; then
    tmux rename-window -t $TMUX_SESSION_NAME:1 'aviportal'
    tmux send-keys -t $TMUX_SESSION_NAME:1 'tail -f /var/log/upstart/aviportal.log' Enter
fi

if [ -f "/opt/avi/log/portal-webapp.log" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'p-webapp'
    tmux send-keys -t $TMUX_SESSION_NAME:2 'tail -f /opt/avi/log/portal-webapp.log' Enter
fi

if [ -f "/var/log/upstart/octavius.log" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'o.log'
    tmux send-keys -t $TMUX_SESSION_NAME:3 'tail -f /var/log/upstart/octavius.log' Enter
fi

if [ -f "/opt/avi/log/octavius.INFO" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'o.INFO'
    tmux send-keys -t $TMUX_SESSION_NAME:4 'tail -f /opt/avi/log/octavius.INFO' Enter
fi

if [ -f "/var/log/upstart/apiserver.log" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'a.log'
    tmux send-keys -t $TMUX_SESSION_NAME:5 'tail -f /var/log/upstart/apiserver.log' Enter
fi

if [ -f "/opt/avi/log/apiserver.INFO" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'a.INFO'
    tmux send-keys -t $TMUX_SESSION_NAME:6 'tail -f /opt/avi/log/apiserver.INFO' Enter
fi

if [ -f "/opt/avi/log/apiserver.DEBUG" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'a.DEBUG'
    tmux send-keys -t $TMUX_SESSION_NAME:7 'tail -f /opt/avi/log/apiserver.DEBUG' Enter
fi

if [ -f "/var/log/nginx/portal.access.log" ]; then
    tmux new-window -t $TMUX_SESSION_NAME -n 'nginx'
    tmux send-keys -t $TMUX_SESSION_NAME:7 'tail -f /var/log/nginx/portal.access.log' Enter
fi

tmux new-window -t $TMUX_SESSION_NAME 

cd ~/
