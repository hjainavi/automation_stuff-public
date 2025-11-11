#!/bin/bash

# Script to check if port 2345 is in use, kill the process using it, and start dlv debugger
# Usage: ./dlv_apiserver.sh

PORT=2345

# Function to start dlv debugger
start_dlv_debugger() {
    echo "Starting dlv debugger..."
    
    # Find the apiserver process ID
    APISERVER_PID=$(ps -ef | awk '/\/bin\/apiserver/{print $2}')
    
    if [ -z "$APISERVER_PID" ]; then
        echo "ERROR: No apiserver process found. Cannot attach debugger."
        exit 1
    fi
    
    echo "Found apiserver process with PID: $APISERVER_PID"
    echo "Starting dlv debugger on port $PORT..."
    
    # Start dlv debugger in direct mode (headless)
    echo "Starting in direct mode (headless)..."
    DLV_CMD="sudo /root/controller_customization_new/dlv --listen=:$PORT --headless=true --api-version=2 attach $APISERVER_PID"
    echo "Executing: $DLV_CMD"
    $DLV_CMD
}

echo "Checking if port $PORT is in use..."

# Find the process using port 2345
# Using lsof to find the process ID
PID=$(lsof -ti :$PORT 2>/dev/null)

if [ -z "$PID" ]; then
    echo "Port $PORT is not in use."
    start_dlv_debugger
else
    echo "Port $PORT is being used by process ID: $PID"
    
    # Get process details for confirmation
    PROCESS_INFO=$(ps -p $PID -o pid,ppid,cmd --no-headers 2>/dev/null)
    
    if [ -n "$PROCESS_INFO" ]; then
        echo "Process details:"
        echo "PID  PPID COMMAND"
        echo "$PROCESS_INFO"
        
        # Kill the process
        echo "Killing process $PID..."
        kill $PID
        
        # Wait a moment and check if process is still running
        sleep 5
        
        if kill -0 $PID 2>/dev/null; then
            echo "Process $PID is still running. Attempting force kill..."
            kill -9 $PID
            sleep 5
            
            if kill -0 $PID 2>/dev/null; then
                echo "ERROR: Failed to kill process $PID"
                exit 1
            else
                echo "Process $PID forcefully killed."
            fi
        else
            echo "Process $PID successfully killed."
        fi
        
        # Verify port is now free
        NEW_PID=$(lsof -ti :$PORT 2>/dev/null)
        if [ -z "$NEW_PID" ]; then
            echo "Port $PORT is now free."
            start_dlv_debugger
        else
            echo "WARNING: Port $PORT is still in use by process $NEW_PID"
            exit 1
        fi
    else
        echo "Process $PID not found in process list."
        echo "Checking if port is now free..."
        NEW_PID=$(lsof -ti :$PORT 2>/dev/null)
        if [ -z "$NEW_PID" ]; then
            echo "Port $PORT is now free."
            start_dlv_debugger
        else
            echo "WARNING: Port $PORT is still in use."
            exit 1
        fi
    fi
fi

