#!/bin/bash

cd ${1:-certificates}

for CERT in $(ls *.cert.pem)
do
    echo === ${CERT}
    openssl x509 -in "${CERT}" -text -noout
done
