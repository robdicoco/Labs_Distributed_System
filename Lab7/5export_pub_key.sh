#!/bin/bash

pkcs11-tool \
  --module /lib/libtacndp11.so \
  --login \
  --pin 1234 \
  --read-object \
  --type pubkey \
  --label code-signing-key \
  --output-file public_key.der