#!/usr/bin/env bash
set -e

DOMAIN=${1:-"example.com"}

openssl genrsa -out "$DOMAIN.key" 4096
openssl req -new -key "$DOMAIN.key" -out "$DOMAIN.csr" <<REQUEST
XX
Everywhere
Somewhere
Myself
Here
$DOMAIN
certificate@$DOMAIN


REQUEST

cat > v3.ext <<EXT
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer:always
basicConstraints       = CA:FALSE
keyUsage               = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment, keyAgreement, keyCertSign
subjectAltName         = DNS:*.$DOMAIN, DNS:$DOMAIN
issuerAltName          = issuer:copy
EXT

openssl x509 -req -in "$DOMAIN.csr" -signkey "$DOMAIN.key" -out "$DOMAIN.crt" -days 3650 -sha256 -extfile v3.ext
rm v3.ext "$DOMAIN.csr"