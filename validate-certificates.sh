#!/bin/bash

cd ${1:-certificates}

for CERT in $(ls *.cert.pem)
do
    if [ "$CERT" == "ca.cert.pem" ]
    then
        continue
    fi

    openssl verify -CAfile ca.cert.pem "${CERT}"
done
