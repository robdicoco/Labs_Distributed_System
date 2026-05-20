#!/bin/bash

openssl dgst \
  -sha256 \
  -engine pkcs11 \
  -keyform engine \
  -sign "pkcs11:token=Dinamo%20HSM;object=code-signing-key;type=private" \
  -out app.py.sig \
  app.py