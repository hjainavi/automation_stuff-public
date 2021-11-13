TMUX_SESSION_NAME='harsh'
tmux new-session -d -s $TMUX_SESSION_NAME >/dev/null
tmux new-window -t $TMUX_SESSION_NAME
tmux send-keys -t $TMUX_SESSION_NAME:1 'tail -f /var/log/upstart/aviportal.log' Enter
tmux new-window -t $TMUX_SESSION_NAME
tmux send-keys -t $TMUX_SESSION_NAME:2 'tail -f /opt/avi/log/portal-webapp.log' Enter
tmux new-window -t $TMUX_SESSION_NAME
tmux send-keys -t $TMUX_SESSION_NAME:3 'tail -f /opt/avi/log/octavius.INFO' Enter
