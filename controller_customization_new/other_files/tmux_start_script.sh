TMUX_SESSION_NAME='harsh'
tmux new-session -d -s $TMUX_SESSION_NAME >/dev/null
tmux new-window -t $TMUX_SESSION_NAME -n 'aviportal'
tmux send-keys -t $TMUX_SESSION_NAME:1 'tail -f /var/log/upstart/aviportal.log' Enter
tmux new-window -t $TMUX_SESSION_NAME -n 'portal-webapp'
tmux send-keys -t $TMUX_SESSION_NAME:2 'tail -f /opt/avi/log/portal-webapp.log' Enter
tmux new-window -t $TMUX_SESSION_NAME -n 'octavius.log'
tmux send-keys -t $TMUX_SESSION_NAME:1 'tail -f /var/log/upstart/octavius.log' Enter
tmux new-window -t $TMUX_SESSION_NAME -n 'octavius.INFO'
tmux send-keys -t $TMUX_SESSION_NAME:3 'tail -f /opt/avi/log/octavius.INFO' Enter
tmux new-window -t $TMUX_SESSION_NAME -n 'apiserver.log'
tmux send-keys -t $TMUX_SESSION_NAME:1 'tail -f /var/log/upstart/apiserver.log' Enter
tmux new-window -t $TMUX_SESSION_NAME -n 'apiserver.INFO'
tmux send-keys -t $TMUX_SESSION_NAME:4 'tail -f /opt/avi/log/apiserver.INFO' Enter
tmux new-window -t $TMUX_SESSION_NAME -n 'apiserver.DEBUG'
tmux send-keys -t $TMUX_SESSION_NAME:4 'tail -f /opt/avi/log/apiserver.DEBUG' Enter
cd ~/
