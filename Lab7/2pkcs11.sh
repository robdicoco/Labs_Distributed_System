#!/bin/bash

pkcs11-tool \
  --module /lib/libtacndp11.so \
  --login --pin 'master:12345678@127.0.0.1' \
  --keypairgen \
  --keygen \
  --key-type RSA:2048 \
  --id 02 \
  --label 'rsa2k' \
  --token-label 'Dinamo HSM'