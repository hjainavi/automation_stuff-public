#!/bin/bash

VALID_ARGS=$(getopt -o :f:u:i:p:d: --long local_file,user,ip,remote_path,identity_file: -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

eval set -- "$VALID_ARGS"
while [ : ]; do
  case "$1" in
    -f | --local_file)
        echo "Processing 'local_file' option. Input argument is '$2'"
        shift 2
        ;;
    -u | --user)
        echo "Processing 'user' option. Input argument is '$2'"
        shift 2
        ;;
    -i | --ip)
        echo "Processing 'ip' option. Input argument is '$2'"
        shift 2
        ;;
    -p | --remote_path)
        echo "Processing 'remote_path' option. Input argument is '$2'"
        shift 2
        ;;
    -d | --identity_file)
        echo "Processing 'identity_file' option. Input argument is '$2'"
        shift 2
        ;;
    :)
      echo "Option -${OPTARG} requires an argument."
      exit 1
      ;;
    --) shift; 
        break 
        ;;
  esac
done

