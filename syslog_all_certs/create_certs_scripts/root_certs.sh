#!/bin/bash

BASEDIR="$( cd "$(dirname "$0")" ; pwd -P )"
echo "$BASEDIR"


#if false
#then

# exit when any command fails
#set -e
#set -x
# keep track of the last executed command
#trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

echo "Create Root key and cert ?(y/n)"
read answer
if [ "$answer" == "y" ]; then
    # ROOT KEY AND CERT
    if [ ! -d "$BASEDIR/ca" ]; then
        mkdir $BASEDIR/ca
    fi

    cd $BASEDIR/ca

    if [ ! -d "certs" ]; then
        mkdir certs crl newcerts private
    fi

    cp $BASEDIR/opensslCA_base.cnf $BASEDIR/opensslCA.cnf
    sed -i "s<^dir.*=.*ca<dir               = $BASEDIR/ca<" $BASEDIR/opensslCA.cnf

    chmod 700 private
    touch index.txt
    echo 1000 > serial
    openssl genrsa -out private/ca.key.pem 2048
    chmod 400 private/ca.key.pem
    openssl req -config $BASEDIR/opensslCA.cnf -key private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out certs/ca.cert.pem
    openssl x509 -noout -text -in certs/ca.cert.pem
fi

echo "Create Intermediate key and cert ?(y/n)"
read answer
if [ "$answer" == "y" ]; then
    if [ -f $BASEDIR/ca/certs/ca.cert.pem ]; then
                
        # INTERMEDIATE KEY AND CERT
        if [ ! -d "$BASEDIR/ca/intermediate" ]; then
            mkdir $BASEDIR/ca/intermediate
        fi
        cd $BASEDIR/ca/intermediate

        if [ ! -d "$BASEDIR/ca/intermediate/certs" ]; then
            mkdir certs csr newcerts private crl
        fi
        chmod 700 private
        touch index.txt
        echo 1000 > serial
        echo 1000 > $BASEDIR/ca/intermediate/crlnumber

        cp $BASEDIR/opensslINTER_base.cnf $BASEDIR/opensslINTER.cnf
        sed -i "s>^dir.*=.*intermediate>dir               = $BASEDIR/ca/intermediate>" $BASEDIR/opensslINTER.cnf
        
        cd $BASEDIR/ca
        openssl genrsa -out intermediate/private/intermediate.key.pem 2048
        chmod 400 intermediate/private/intermediate.key.pem
        openssl req -config $BASEDIR/opensslINTER.cnf -new -sha256 -key intermediate/private/intermediate.key.pem -out intermediate/csr/intermediate.csr.pem

        openssl ca -config $BASEDIR/opensslCA.cnf -extensions v3_intermediate_ca -days 7329 -notext -md sha256 -in intermediate/csr/intermediate.csr.pem -out intermediate/certs/intermediate.cert.pem

        chmod 444 intermediate/certs/intermediate.cert.pem
        openssl x509 -noout -text -in intermediate/certs/intermediate.cert.pem
        openssl verify -CAfile certs/ca.cert.pem intermediate/certs/intermediate.cert.pem
        cat intermediate/certs/intermediate.cert.pem certs/ca.cert.pem > intermediate/certs/ca-chain.cert.pem
        chmod 444 intermediate/certs/ca-chain.cert.pem
    else
        echo "ROOT CA and CERT not created. Please Create"
        exit 1
    fi
fi


echo "Create Server key and cert ?(y/n)"
read server_cert_answer
if [ "$server_cert_answer" == "y" ]; then
    if [ -f $BASEDIR/ca/intermediate/certs/intermediate.cert.pem ]; then
        cd $BASEDIR/ca
        openssl genrsa -out intermediate/private/www.server.com.key.pem 1024
        chmod 444 intermediate/private/www.server.com.key.pem
        openssl req -config $BASEDIR/opensslINTER.cnf -key intermediate/private/www.server.com.key.pem -new -sha256 -out intermediate/csr/www.server.com.csr.pem
        openssl ca -config $BASEDIR/opensslINTER.cnf -extensions server_cert -days 7328 -notext -md sha256 -in intermediate/csr/www.server.com.csr.pem -out intermediate/certs/www.server.com.cert.pem
        chmod 444 intermediate/certs/www.server.com.cert.pem
        openssl verify -CAfile intermediate/certs/ca-chain.cert.pem intermediate/certs/www.server.com.cert.pem

    else
        echo "INTERMEDIATE CA and CERT not created. Please Create"
        exit 1
    fi
fi


echo "Create Client key and cert ?(y/n)"
read client_cert_answer
if [ "$client_cert_answer" == "y" ]; then
    if [ -f $BASEDIR/ca/intermediate/certs/intermediate.cert.pem ]; then
        cd $BASEDIR/ca
        openssl genrsa -out intermediate/private/www.client.com.key.pem 1024
        chmod 444 intermediate/private/www.client.com.key.pem
        openssl req -config $BASEDIR/opensslINTER.cnf -key intermediate/private/www.client.com.key.pem -new -sha256 -out intermediate/csr/www.client.com.csr.pem
        openssl ca -config $BASEDIR/opensslINTER.cnf -extensions usr_cert -days 7328 -notext -md sha256 -in intermediate/csr/www.client.com.csr.pem -out intermediate/certs/www.client.com.cert.pem
        chmod 444 intermediate/certs/www.client.com.cert.pem
        openssl verify -CAfile intermediate/certs/ca-chain.cert.pem intermediate/certs/www.client.com.cert.pem

    else
        echo "INTERMEDIATE CA and CERT not created. Please Create"
        exit 1
    fi
fi

echo " CA file name ? "
read ca_file_name
echo " Inter CA file name ? "
read inter_file_name

if [ -f $BASEDIR/ca/intermediate/certs/www.client.com.cert.pem ]; then
    echo " Client cert name ? "
    read client_file_name
fi

if [ -f $BASEDIR/ca/intermediate/certs/www.server.com.cert.pem ]; then
    echo " Server cert name ? "
    read server_file_name
fi

key="_key.pem"
cert="_cert.pem"
ca_chain="_ca_chain_cert.pem"
cd $BASEDIR
if [ ! -d "$BASEDIR/allcerts" ]; then
    mkdir $BASEDIR/allcerts
fi
ca_cert="$ca_file_name$cert"
ca_key="$ca_file_name$key"
inter_cert="$inter_file_name$cert"
inter_key="$inter_file_name$key"
if [ -f $BASEDIR/ca/intermediate/certs/www.server.com.cert.pem ]; then
    server_cert="$server_file_name$cert"
    server_key="$server_file_name$key"
fi

if [ -f $BASEDIR/ca/intermediate/certs/www.client.com.cert.pem ]; then
    client_cert="$client_file_name$cert"
    client_key="$client_file_name$key"
fi
ca_chain_cert="$ca_file_name$ca_chain"

cp ca/certs/ca.cert.pem ./allcerts/$ca_cert
cp ca/private/ca.key.pem ./allcerts/$ca_key
cp ca/intermediate/certs/intermediate.cert.pem ./allcerts/$inter_cert
cp ca/intermediate/certs/ca-chain.cert.pem ./allcerts/$ca_chain_cert
cp ca/intermediate/private/intermediate.key.pem ./allcerts/$inter_key
if [ -f $BASEDIR/ca/intermediate/certs/www.server.com.cert.pem ]; then
    cp ca/intermediate/certs/www.server.com.cert.pem ./allcerts/$server_cert
    cp ca/intermediate/private/www.server.com.key.pem ./allcerts/$server_key
fi
if [ -f $BASEDIR/ca/intermediate/certs/www.client.com.cert.pem ]; then
    cp ca/intermediate/certs/www.client.com.cert.pem ./allcerts/$client_cert
    cp ca/intermediate/private/www.client.com.key.pem ./allcerts/$client_key
fi
echo "ALL FILES IN $BASEDIR/allcerts folder"

echo "Delete all data ?(y/n)"
read answer
if [ "$answer" == "y" ]; then
    rm -r $BASEDIR/ca
fi
