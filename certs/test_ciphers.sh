#!/usr/bin/env bash
# ------- protocol -- tls1 , tls1_1 , tls1_2
# OpenSSL requires the port number.
SERVER=$1
DELAY=0.2
#ciphers=$(openssl ciphers 'AES256-SHA' | sed -e 's/:/ /g')
#ciphers=$(openssl ciphers 'kECDH' | sed -e 's/:/ /g')
ciphers=$(openssl ciphers $3 | sed -e 's/:/ /g')
PROTOCOL=$2
echo Obtaining cipher list from $(openssl version).

for cipher in ${ciphers[@]}
do
#echo -n Testing $cipher...
result=$(echo -n | openssl s_client -$2 -cipher "$cipher" -connect $SERVER 2>&1)
if [[ "$result" =~ ":error:" ]] ; then
  error=$(echo -n $result | cut -d':' -f6)
  #echo NO \($error\)
else
  if [[ "$result" =~ "Cipher is ${cipher}" || "$result" =~ "Cipher    :" ]] ; then
    echo -n "$cipher",
  else
    echo UNKNOWN RESPONSE
    echo $result
  fi
fi
#sleep $DELAY
done
echo
