#!/bin/bash

openssl dgst \
  -sha256 \
  -verify public_key.pem \
  -signature app.py.sig \
  app.py