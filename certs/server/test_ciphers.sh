#!/usr/bin/env bash

# OpenSSL requires the port number.
SERVER=$1
DELAY=0.2
ciphers=$(openssl ciphers 'ALL' | sed -e 's/:/ /g')
PROTOCOL=$2
#echo Obtaining cipher list from $(openssl version).
#echo List of compatible ciphers
for cipher in ${ciphers[@]}
do
#echo -n Testing $cipher...
result=$(echo -n | openssl s_client -$2 -cipher "$cipher" -connect $SERVER 2>&1)
if [[ "$result" =~ ":error:" ]] ; then
  error=$(echo -n $result | cut -d':' -f6)
  #echo NO \($error\)
else
  if [[ "$result" =~ "Cipher is ${cipher}" || "$result" =~ "Cipher    :" ]] ; then
    echo $cipher
  else
    echo UNKNOWN RESPONSE
    echo $result
  fi
fi
#sleep $DELAY
done
